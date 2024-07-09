from sparkai.llm.llm import ChatSparkLLM, ChunkPrintHandler
from sparkai.core.messages import ChatMessage
from .import sparkVoice

#星火认知大模型Spark Max的URL值，其他版本大模型URL值请前往文档（https://www.xfyun.cn/doc/spark/Web.html）查看
SPARKAI_URL = 'wss://spark-api.xf-yun.com/v3.5/chat'
#星火认知大模型调用秘钥信息，请前往讯飞开放平台控制台（https://console.xfyun.cn/services/bm35）查看
SPARKAI_APP_ID = 'd8037aee'
SPARKAI_API_SECRET = 'OWYzYmU3NzgxMzNkYmFlNWJlNTgxNzNh'
SPARKAI_API_KEY = '3ccb2190cdab6a40aefd96c623875967'
#星火认知大模型Spark Max的domain值，其他版本大模型domain值请前往文档（https://www.xfyun.cn/doc/spark/Web.html）查看
SPARKAI_DOMAIN = 'generalv3.5'

default_messages = [ChatMessage(
        role= "system",
        content= "你是网盘助手懒子哥",
    )]

class SparkAIModel:
    def __init__(self):
        self.messages = default_messages

    def spark_mul_chat(self,message):
        spark = ChatSparkLLM(
            
            spark_api_url=SPARKAI_URL,
            spark_app_id=SPARKAI_APP_ID,
            spark_api_key=SPARKAI_API_KEY,
            spark_api_secret=SPARKAI_API_SECRET,
            spark_llm_domain=SPARKAI_DOMAIN,
            streaming=False,
        )
        
        self.messages.append(ChatMessage(
                role= "user",
                content= message,
        ))

        handler = ChunkPrintHandler()
        result = spark.generate([self.messages], callbacks=[handler]).generations[0][0].text

        self.messages.append(ChatMessage(
                role= "assistant",
                content= result,
        ))

        print(result)
        return result
    
    def spark_AI_voice(self,text:str):
        return sparkVoice.sparkAIvoice(text)

# if __name__ == '__main__':
#     while True:
#         message = input()
#         s1 = SparkAIModel()
#         s1.spark_mul_chat(message)