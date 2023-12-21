import requests
from openai import OpenAI
from time import sleep
import threading
import re

class WeChat:

    def __init__(self):
        self.BASE_URL = 'http://127.0.0.1:52700/wechat-plugin/'
        # [GET] 最近聊天列表，可选参数: [keyword]
        self.USER_URL = self.BASE_URL + 'user'
        # [GET] 根据用户 id 查询指定数量聊天记录，可选参数：[userId, count]
        self.CHAT_LOG_URL = self.BASE_URL + 'chatlog'
        # [POST] 根据用户 id 发送消息，可选参数：[userId, content, srvId]（Content-Type: application/x-www-form-urlencoded）
        self.SEND_MESSAGE_URL = self.BASE_URL + 'send-message'
        # [POST] 打开与指定好友的聊天窗口，参数：[userId]（Content-Type: application/x-www-form-urlencoded）
        self.OPEN_SESSION_URL = self.BASE_URL + 'open-session'

    def _get_user_id_by_name(self, users, name):
        """根据名称获取 userId

        Args:
            users (list): 用户字典列表
            name (str): 待匹配的名称

        Return:
            list: 待匹配名称对应 userId
        """
        return [
            user['userId']
            for user in users
            if name == user['title'].replace('[群聊]', '').split('(')[0]
        ]

    def search_user_by_keyword(self, keyword):
        """根据关键词搜索用户

        Args:
            keyword (str): 关键词

        Returns:
            dict: 用户相关信息列表
        """
        return requests.get(self.USER_URL, params={"keyword": keyword}).json()

    def search_user_by_name(self, name, group=False):
        """根据名称获取 userId

        Args:
            name (str): 待匹配的名称
            group (bool, optional): 是否多选，默认为 False，若 False 在匹配多个情况下默认返回最近的联系人

        Returns:
            list: userId 列表
        """
        r = requests.get(self.USER_URL).json()
        user_ids = self._get_user_id_by_name(r, name)
        if not user_ids:
            return []
        if group:
            return user_ids
        else:
            return [user_ids[0]]

    def get_chat_log_by_name(self, name, count):
        """根据待匹配名称获取聊天记录

        Args:
            name (str): 用户 userId
            count (int): 返回聊天记录条目数

        Raises:
            ValueError: 待匹配名称重复，例如有两个相同的人名

        Returns:
            dict: 聊天记录字典
        """
        user_ids = self.search_user_by_name(name, group=True)
        if len(user_ids) > 1:
            raise ValueError("用户 ID 数量大于 1，请检查是否同名")
        r = requests.get(self.CHAT_LOG_URL, params={
                         "userId": user_ids, "count": count})
        if r:
            return {i['subTitle']: i['copyText'] for i in r.json()[:0:-1]}
        else:
            return {}

    def get_chat_log_by_id(self, user_id, count):
        """根据 userId 获取聊天记录

        Args:
            user_id (int): 用户 userId
            count (int): 返回聊天记录条目数

        Returns:
            dict: 聊天记录字典
        """
        r = requests.get(self.CHAT_LOG_URL, params={
                         "userId": user_id, "count": count})
        if r:
            return {i['subTitle']: i['copyText'] for i in r.json()[:0:-1]}
        else:
            return {}

    def send_message_by_name(self, name, content, srvId=1, group=False):
        """通过待匹配名称发送消息

        Args:
            name (str): 待匹配名称
            content (str): 待发送的消息
            srvId (int, optional): Defaults to 1.
            group (bool, optional): 是否群发，默认 False

        Returns:
            bool: 布尔值
        """
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }
        user_ids = self.search_user_by_name(name, group=group)
        for user_id in user_ids:
            r = requests.post(self.SEND_MESSAGE_URL, headers=headers, data={
                              "userId": user_id, "content": content, "srvId": srvId})
        return True

    def send_message_by_ids(self, user_ids, content, srvId=1):
        """通过 userId 发送消息

        Args:
            user_ids (list): 需要发送消息的 userId 列表
            content (str): 待发送的消息
            srvId (int, optional): [int]. Defaults to 1.

        Returns:
            bool: 布尔值
        """
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }
        for user_id in user_ids:
            r = requests.post(self.SEND_MESSAGE_URL, headers=headers, data={
                              "userId": user_id, "content": content, "srvId": srvId})
        return True

class WeChatClient:
    def __init__(self):
        pass
    def handle_user_id(self, user_id):
        # create a thread
        message_thread = client.beta.threads.create(
            messages=[]
        )
        me_last_index = None
        messages_after_my_index = []

        while True:
            chat_logs = wechat.get_chat_log_by_id(user_id, 5)
            # 将消息转换为列表形式，以便使用索引
            messages_list = list(chat_logs.items())

            # 找到Jack_sit_的最後一條消息的索引
            for index, (message_key, message) in enumerate(messages_list):
                if my_name in message_key:
                    me_last_index = index

            # 提取在Jack_sit_最後一條消息之後的所有來自的消息
            if me_last_index:
                messages_after_my_index = [
                    message for time_key, message in messages_list[me_last_index + 1:]
                ]

            for message in messages_after_my_index:
                if '/' in message:
                    messages_after_my_index.remove(message)
                    messages_after_my_index.append('（對方傳來一個貼圖）請按先前對話內容發訊息')

            if messages_after_my_index:
                print(user_id,messages_after_my_index)
                self.reply_message(user_id, message_thread.id, messages_after_my_index)

            sleep(5)
    def send_messages(self, user, reply_msg):
        # 使用正则表达式来分割消息
        sentences = re.split(r'[。？！!?.]', reply_msg)
        # 定义要替换的词汇和替换文本的字典
        word_replacements = {
            '朋友': 'frd',
            '，': ' ',
        }
        # 替换特定词汇
        for i, sentence in enumerate(sentences):
            for word, replacement in word_replacements.items():
                sentence = sentence.replace(word, replacement)
            sentences[i] = sentence

        # 逐句发送消息
        for sentence in sentences:
            # sleep(len(sentence)*0.3)
            wechat.send_message_by_ids([user], sentence)
    def reply_message(self, user, thread_id, message):
        # message
        client.beta.threads.messages.create(
            thread_id=thread_id,  # thread_id before
            role='user',
            content=str(message),
        )

        # run
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=my_assistant.id
        )

        # Initialize a variable to keep track of the run status
        run_status = None

        # Continuously check the run status
        while run_status != 'completed':
            # Retrieve the latest run status
            run = client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id
            )
            run_status = run.status

            # Print the current status
            print(f"Current status: {run_status}")

            # If the run is completed, retrieve and print messages
            if run_status == 'completed':
                receive_messages = client.beta.threads.messages.list(thread_id)
                reply_msg = receive_messages.data[0].content[0].text.value
                print(receive_messages.data[0].content[0].text.value)
                self.send_messages(user, reply_msg)
            elif run_status == 'failed':
                # message
                client.beta.threads.messages.create(
                    thread_id=thread_id,  # thread_id before
                    role='user',
                    content=str(message),
                )

                # run
                run = client.beta.threads.runs.create(
                    thread_id=thread_id,
                    assistant_id=my_assistant.id
                )
            # Optional: add a sleep interval to avoid overwhelming the server
            sleep(5)  # Waits for 10 second before the next status check

        # Outside the while loop
        print("Run has completed.")


if __name__ == '__main__':
    wechat_client = WeChatClient()
    wechat = WeChat()
    client = OpenAI(
        api_key="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",
    )
    my_assistant = client.beta.assistants.retrieve("asst_3TIBwVoM2wKCNIueJiyuUNRO")
    print(my_assistant)
    my_name='Jack_sit_'

    # 假设你有一个用户ID列表
    user_ids = ['']

    # 为每个用户创建一个线程
    for user_id in user_ids:
        threading.Thread(target=wechat_client.handle_user_id, args=(user_id,)).start()
    print('listening...')