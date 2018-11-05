from elasticsearch_dsl import Document, Keyword, Text

from elasticsearch_dsl.connections import connections
# Define a default Elasticsearch client
connections.create_connection(hosts=['localhost'])

class IndeedType(Document):
    #要保存在elasticsearch中的数据类型
    job_title = Text(analyzer="ik_max_word")
    job_location = Text(analyzer="ik_max_word")
    job_summary = Text(analyzer="ik_max_word")
    job_salary = Text(analyzer="ik_max_word")
    company_name = Text(analyzer="ik_max_word")
    job_href = Text(analyzer="ik_max_word")
    job_star = Text(analyzer="ik_max_word")
    job_review = Text(analyzer="ik_max_word")


    class Meta:
        index = "Indeed"
        doc_type = "data_science"

    class Index:
        name = "indeed"
        doc_type = "data_science"

    # Display cluster health
    print(connections.get_connection().cluster.health())


if __name__ == "__main__":
    IndeedType.init()
