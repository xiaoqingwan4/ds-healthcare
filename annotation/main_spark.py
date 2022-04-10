from annotation.annotation_utils.annotation_util import read_nlp_model_config, read_annotation_config
from annotation.components.annotator import pudf_annotate
from utils.resource_util import get_data_filepath
from utils.spark_util import get_spark_session, write_dataframe_to_dir, add_repo_pyfile
import pyspark.sql.functions as F
from pathlib import Path
import os

if __name__ == "__main__":
    nlp_model_config_filepath = os.path.join(Path(__file__).parent, "conf/nlp_model_template.cfg")
    nlp_model_config = read_nlp_model_config(nlp_model_config_filepath)

    annotation_config_filepath = os.path.join(Path(__file__).parent, "conf/annotation_template.cfg")
    annotation_config = read_annotation_config(annotation_config_filepath)

    domain_dir = get_data_filepath(annotation_config["domain"])
    input_filepath = os.path.join(domain_dir, "input", "drug_reivews.json")

    spark = get_spark_session("test", master_config="local[4]", log_level="INFO")
    add_repo_pyfile(spark)

    input_df = spark.read.text(input_filepath).repartition(4)
    annotation_df = input_df.select(pudf_annotate(F.col("value"), nlp_model_config))
    write_dataframe_to_dir(annotation_df, domain_dir, annotation_config["annotation_folder"], file_format="txt")