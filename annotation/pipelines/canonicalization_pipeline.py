from typing import Dict, Any
from annotation.annotation_utils.annotator_util import read_annotation_config, get_canonicalization_nlp_model_config
from annotation.components.annotator import pudf_annotate, load_annotation
from annotation.components.canonicalizer import get_canonicalization
from annotation.components.canonicalizer_bigram import get_bigram_canonicalization_candidates, \
    get_bigram_canonicalization_candidates_match_dict, get_bigram_canonicalization
from annotation.components.canonicalizer_spell import get_spell_canonicalization_candidates, get_spell_canonicalization
from annotation.components.extractor import extract_unigram, extract_ngram
from word_vector.wv_corpus import extact_wv_corpus_from_annotation
from word_vector.wv_model import build_word2vec
from utils.resource_util import get_data_filepath
from utils.spark_util import get_spark_session, add_repo_pyfile, write_sdf_to_dir
from utils.log_util import get_logger
from pyspark.sql import SparkSession, DataFrame
import pyspark.sql.functions as F
import argparse
import os


def load_input_and_build_canonicalization_annotation(spark: SparkSession,
                                                     input_filepath: str,
                                                     input_dir: str,
                                                     canonicalization_dir: str,
                                                     canonicalization_nlp_model_config: Dict[str, Dict[str, Any]],
                                                     annotation_config: Dict[str, str]) -> DataFrame:
    logger.info(f"\n{'=' * 100}\nload input and build canonicalization annotation\n{'=' * 100}\n")
    if input_filepath:
        input_sdf = spark.read.text(input_filepath)
    if input_dir:
        input_sdf = spark.read.text(os.path.join(input_dir, "*.json"))
    num_partitions = annotation_config["num_partitions"]
    input_sdf = input_sdf.repartition(num_partitions).cache()
    canonicalization_annotation_sdf = input_sdf.select(pudf_annotate(F.col("value"), canonicalization_nlp_model_config))
    write_sdf_to_dir(canonicalization_annotation_sdf, canonicalization_dir,
                     annotation_config["canonicalization_annotation_folder"], file_format="txt")


def build_extraction_and_canonicalization_candidates(canonicalization_annotation_sdf: DataFrame,
                                                     canonicalization_unigram_filepath: str,
                                                     canonicalization_bigram_filepath: str,
                                                     canonicalization_trigram_filepath: str,
                                                     bigram_canonicalization_candidates_filepath: str,
                                                     spell_canonicalization_candidates_filepath: str,
                                                     annotation_config: Dict[str, Any]):
    logger.info(f"\n{'=' * 100}\nextract unigram, bigram and trigram and "
                f"build bigram & spell canonicalization candidates\n{'=' * 100}\n")
    unigram_sdf = extract_unigram(canonicalization_annotation_sdf, canonicalization_unigram_filepath)
    bigram_sdf = extract_ngram(canonicalization_annotation_sdf, canonicalization_bigram_filepath,
                               n=2, ngram_filter_min_count=annotation_config["ngram_filter_min_count"])
    extract_ngram(canonicalization_annotation_sdf, canonicalization_trigram_filepath,
                  n=3, ngram_filter_min_count=annotation_config["ngram_filter_min_count"])
    get_bigram_canonicalization_candidates(unigram_sdf,
                                           bigram_sdf,
                                           bigram_canonicalization_candidates_filepath)
    get_spell_canonicalization_candidates(unigram_sdf,
                                          canonicalization_annotation_sdf,
                                          spell_canonicalization_candidates_filepath,
                                          annotation_config["spell_canonicalization_suggestion_filter_min_count"])


def build_word_vector_corpus(canonicalization_annotation_sdf: DataFrame,
                             bigram_canonicalization_candidates_filepath: str,
                             wv_corpus_filepath: str,
                             canonicalization_nlp_model_config: str,
                             annotation_config: Dict[str, Any]):
    logger.info(f"\n{'=' * 100}\nbuild word vector corpus\n{'=' * 100}\n")
    match_lowercase = annotation_config["wv_corpus_match_lowercase"]
    ngram_match_dict = get_bigram_canonicalization_candidates_match_dict(
        bigram_canonicalization_candidates_filepath, match_lowercase)
    extact_wv_corpus_from_annotation(
        annotation_sdf=canonicalization_annotation_sdf,
        lang=canonicalization_nlp_model_config["lang"],
        spacy_package=canonicalization_nlp_model_config["spacy_package"],
        wv_corpus_filepath=wv_corpus_filepath,
        ngram_match_dict=ngram_match_dict,
        match_lowercase=match_lowercase,
        num_partitions=4)


def build_canonicalization(spark: SparkSession,
                           canonicalization_unigram_filepath: str,
                           canonicalization_bigram_filepath: str,
                           canonicalization_trigram_filepath: str,
                           bigram_canonicalization_candidates_filepath: str,
                           spell_canonicalization_candidates_filepath: str,
                           bigram_canonicalization_filepath: str,
                           spell_canonicalization_filepath: str,
                           canonicalization_filepath: str,
                           wv_model_filepath: str,
                           annotation_config: Dict[str, Any]):
    logger.info(f"\n{'=' * 100}\nbuild bigram, spell, prefix, hyphen and ampersand canonicalization\n{'=' * 100}\n")
    spell_canonicalization_candidates_sdf = spark.read.csv(
        spell_canonicalization_candidates_filepath, header=True, quote='"', escape='"', inferSchema=True)
    wv_model_filepath = os.path.join(wv_model_filepath.rsplit(".", 1)[0], "fasttext")
    get_bigram_canonicalization(bigram_canonicalization_candidates_filepath,
                                wv_model_filepath,
                                bigram_canonicalization_filepath,
                                annotation_config["wv_bigram_canonicalization_filter_min_similarity"])

    get_spell_canonicalization(spell_canonicalization_candidates_sdf,
                               canonicalization_unigram_filepath,
                               wv_model_filepath,
                               spell_canonicalization_filepath,
                               annotation_config["spell_canonicalization_suggestion_filter_min_count"],
                               annotation_config["spell_canonicalization_edit_distance_filter_max_count"],
                               annotation_config["spell_canonicalization_misspelling_filter_max_percent"],
                               annotation_config["spell_canonicalization_word_pos_filter_min_percent"],
                               annotation_config["wv_spell_canonicalization_filter_min_similarity"])

    get_canonicalization(bigram_canonicalization_filepath,
                         spell_canonicalization_filepath,
                         canonicalization_unigram_filepath,
                         canonicalization_bigram_filepath,
                         canonicalization_trigram_filepath,
                         canonicalization_filepath,
                         annotation_config["conjunction_trigram_canonicalization_filter_min_count"])


def main(spark: SparkSession,
         nlp_model_config_filepath: str,
         annotation_config_filepath: str,
         input_filepath: str,
         input_dir: str):
    canonicalization_nlp_model_config = get_canonicalization_nlp_model_config(nlp_model_config_filepath)
    annotation_config = read_annotation_config(annotation_config_filepath)

    domain_dir = get_data_filepath(annotation_config["domain"])
    canonicalization_dir = os.path.join(domain_dir, annotation_config["canonicalization_folder"])
    canonicalization_annotation_dir = os.path.join(
        canonicalization_dir, annotation_config["canonicalization_annotation_folder"])
    canonicalization_extraction_dir = os.path.join(
        canonicalization_dir, annotation_config["canonicalization_extraction_folder"])
    canonicalization_wv_dir = os.path.join(
        canonicalization_dir, annotation_config["canonicalization_wv_folder"])
    canonicalization_unigram_filepath = os.path.join(
        canonicalization_extraction_dir, annotation_config["canonicalization_unigram_filename"])
    canonicalization_bigram_filepath = os.path.join(
        canonicalization_extraction_dir, annotation_config["canonicalization_bigram_filename"])
    canonicalization_trigram_filepath = os.path.join(
        canonicalization_extraction_dir, annotation_config["canonicalization_trigram_filename"])
    bigram_canonicalization_candidates_filepath = os.path.join(
        canonicalization_extraction_dir, annotation_config["bigram_canonicalization_candidates_filename"])
    spell_canonicalization_candidates_filepath = os.path.join(
        canonicalization_extraction_dir, annotation_config["spell_canonicalization_candidates_filename"])
    wv_corpus_filepath = os.path.join(
        canonicalization_wv_dir, annotation_config["canonicalization_wv_corpus_filename"])
    wv_model_filepath = os.path.join(
        canonicalization_wv_dir, annotation_config["canonicalization_wv_model_filename"])
    bigram_canonicalization_filepath = os.path.join(
        canonicalization_extraction_dir, annotation_config["bigram_canonicalization_filename"])
    spell_canonicalization_filepath = os.path.join(
        canonicalization_extraction_dir, annotation_config["spell_canonicalization_filename"])
    canonicalization_filepath = os.path.join(
        canonicalization_dir, annotation_config["canonicalization_filename"])

    load_input_and_build_canonicalization_annotation(spark,
                                                     input_filepath,
                                                     input_dir,
                                                     canonicalization_dir,
                                                     canonicalization_nlp_model_config,
                                                     annotation_config)

    canonicalization_annotation_sdf = load_annotation(spark,
                                                      canonicalization_annotation_dir,
                                                      annotation_config["drop_non_english"])

    build_extraction_and_canonicalization_candidates(canonicalization_annotation_sdf,
                                                     canonicalization_unigram_filepath,
                                                     canonicalization_bigram_filepath,
                                                     canonicalization_trigram_filepath,
                                                     bigram_canonicalization_candidates_filepath,
                                                     spell_canonicalization_candidates_filepath,
                                                     annotation_config)

    build_word_vector_corpus(canonicalization_annotation_sdf,
                             bigram_canonicalization_candidates_filepath,
                             wv_corpus_filepath,
                             canonicalization_nlp_model_config,
                             annotation_config)

    build_word2vec(vector_size=annotation_config["word_vector_size"],
                   use_char_ngram=True,
                   wv_corpus_filepath=wv_corpus_filepath,
                   wv_model_filepath=wv_model_filepath)

    build_canonicalization(spark,
                           canonicalization_unigram_filepath,
                           canonicalization_bigram_filepath,
                           canonicalization_trigram_filepath,
                           bigram_canonicalization_candidates_filepath,
                           spell_canonicalization_candidates_filepath,
                           bigram_canonicalization_filepath,
                           spell_canonicalization_filepath,
                           canonicalization_filepath,
                           wv_model_filepath,
                           annotation_config)


if __name__ == "__main__":
    logger = get_logger()
    parser = argparse.ArgumentParser()
    parser.add_argument("--nlp_model_conf", default="conf/nlp_model_template.cfg", required=False)
    parser.add_argument("--annotation_conf", default="conf/annotation_template.cfg", required=False)
    parser.add_argument("--input_filepath", default=None, required=False)
    parser.add_argument("--input_dir", default=None, required=False)

    nlp_model_config_filepath = parser.parse_args().nlp_model_conf
    annotation_config_filepath = parser.parse_args().annotation_conf
    input_filepath = parser.parse_args().input_filepath
    input_dir = parser.parse_args().input_dir

    master_config = "local[4]"
    spark = get_spark_session("canonicalization", master_config=master_config, log_level="WARN")
    add_repo_pyfile(spark)

    main(spark, nlp_model_config_filepath, annotation_config_filepath, input_filepath, input_dir)
