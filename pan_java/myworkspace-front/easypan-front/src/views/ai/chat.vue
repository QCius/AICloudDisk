<template>
    <div class="container">
      <!-- <div class="header" @click="clickConfig()">
        <div class="title">ChatGPT</div>
        <div class="subtitle">
          基于 OpenAI 的 ChatGPT 自然语言模型人工智能对话
        </div>
        <div class="settings">设置</div>
      </div> -->
  
      <div class="chat-list" ref="chatListDom">
        <div class="chat-item" v-for="item of messageList.filter((v) => v.role !== 'system')">
          <div class="chat-header">
            <div class="role">{{ roleAlias[item.role] }}：</div>
            <Copy class="copy-button" :content="item.content" />
          </div>
          <div class="chat-content">
            <div class="content-text" v-if="item.content" v-html="md.render(item.content)">
            </div>
            <Loding v-else />
          </div>
        </div>
      </div>
  
      <div class="input-container">
        <div v-if="isConfig" class="config-text">请输入 API Key：</div>
        <div class="input-wrapper">
          <input
            class="input"
            :type="isConfig ? 'password' : 'text'"
            :placeholder="isConfig ? 'sk-xxxxxxxxxx' : '请输入'"
            v-model="messageContent"
            @keydown.enter="isTalking || sendOrSave()"
          />
          <button class="button" :disabled="isTalking" @click="sendOrSave()">
            {{ isConfig ? "保存" : "发送" }}
          </button>
        </div>
      </div>
    </div>
  </template>
  
  <script setup lang="ts">
  import type { ChatMessage } from "@/types";
  import { ref, watch, nextTick, onMounted } from "vue";
  import { chat } from "@/libs/gpt";
  import cryptoJS from "crypto-js";
  import Loding from "@/components/Loding.vue";
  import Copy from "@/components/Copy.vue";
  import { md } from "@/libs/markdown";
  
  let apiKey = "";
  let isConfig = ref(true);
  let isTalking = ref(false);
  let messageContent = ref("");
  const chatListDom = ref<HTMLDivElement>();
  const decoder = new TextDecoder("utf-8");
  const roleAlias = { user: "ME", assistant: "ChatGPT", system: "System" };
  const messageList = ref<ChatMessage[]>([
    {
      role: "system",
      content: "你是 ChatGPT，OpenAI 训练的大型语言模型，尽可能简洁地回答。",
    },
    {
      role: "assistant",
      content: `你好，我是AI语言模型，我可以提供一些常用服务和信息，例如：
  
  1. 翻译：我可以把中文翻译成英文，英文翻译成中文，还有其他一些语言翻译，比如法语、日语、西班牙语等。
  
  2. 咨询服务：如果你有任何问题需要咨询，例如健康、法律、投资等方面，我可以尽可能为你提供帮助。
  
  3. 闲聊：如果你感到寂寞或无聊，我们可以聊一些有趣的话题，以减轻你的压力。
  
  请告诉我你需要哪方面的帮助，我会根据你的需求给你提供相应的信息和建议。`,
    },
  ]);
  
  onMounted(() => {
    if (getAPIKey()) {
      switchConfigStatus();
    }
  });
  
  const sendChatMessage = async (content: string = messageContent.value) => {
    try {
      isTalking.value = true;
      if (messageList.value.length === 2) {
        messageList.value.pop();
      }
      messageList.value.push({ role: "user", content });
      clearMessageContent();
      messageList.value.push({ role: "assistant", content: "" });
  
      const { body, status } = await chat(messageList.value, getAPIKey());
      if (body) {
        const reader = body.getReader();
        await readStream(reader, status);
      }
    } catch (error: any) {
      appendLastMessageContent(error);
    } finally {
      isTalking.value = false;
    }
  };
  
  const readStream = async (
    reader: ReadableStreamDefaultReader<Uint8Array>,
    status: number
  ) => {
    let partialLine = "";
  
    while (true) {
      // eslint-disable-next-line no-await-in-loop
      const { value, done } = await reader.read();
      if (done) break;
  
      const decodedText = decoder.decode(value, { stream: true });
  
      if (status !== 200) {
        const json = JSON.parse(decodedText); // start with "data: "
        const content = json.error.message ?? decodedText;
        appendLastMessageContent(content);
        return;
      }
  
      const chunk = partialLine + decodedText;
      const newLines = chunk.split(/\r?\n/);
  
      partialLine = newLines.pop() ?? "";
  
      for (const line of newLines) {
        if (line.length === 0) continue; // ignore empty message
        if (line.startsWith(":")) continue; // ignore sse comment message
        if (line === "data: [DONE]") return; //
  
        const json = JSON.parse(line.substring(6)); // start with "data: "
        const content =
          status === 200
            ? json.choices[0].delta.content ?? ""
            : json.error.message;
        appendLastMessageContent(content);
      }
    }
  };
  
  const appendLastMessageContent = (content: string) =>
    (messageList.value[messageList.value.length - 1].content += content);
  
  const sendOrSave = () => {
    if (!messageContent.value.length) return;
    if (isConfig.value) {
      if (saveAPIKey(messageContent.value.trim())) {
        switchConfigStatus();
      }
      clearMessageContent();
    } else {
      sendChatMessage();
    }
  };
  
  const clickConfig = () => {
    if (!isConfig.value) {
      messageContent.value = getAPIKey();
    } else {
      clearMessageContent();
    }
    switchConfigStatus();
  };
  
  const getSecretKey = () => "lianginx";
  
  const saveAPIKey = (apiKey: string) => {
    if (apiKey.slice(0, 3) !== "sk-" || apiKey.length !== 51) {
      alert("API Key 错误，请检查后重新输入！");
      return false;
    }
    const aesAPIKey = cryptoJS.AES.encrypt(apiKey, getSecretKey()).toString();
    localStorage.setItem("apiKey", aesAPIKey);
    return true;
  };
  
  const getAPIKey = () => {
    if (apiKey) return apiKey;
    const aesAPIKey = localStorage.getItem("apiKey") ?? "";
    apiKey = cryptoJS.AES.decrypt(aesAPIKey, getSecretKey()).toString(
      cryptoJS.enc.Utf8
    );
    return apiKey;
  };
  
  const switchConfigStatus = () => (isConfig.value = !isConfig.value);
  
  const clearMessageContent = () => (messageContent.value = "");
  
  const scrollToBottom = () => {
    if (!chatListDom.value) return;
    scrollTo(0, chatListDom.value.scrollHeight);
  };
  
  watch(messageList.value, () => nextTick(() => scrollToBottom()));
  </script>
  
  <style scoped>
  .container {
    display: flex;
    flex-direction: column;
    height: 100vh;
  }
  
  .header {
    display: flex;
    align-items: baseline;
    width: 100%;
    padding: 1rem 1.5rem;
    background-color: #f7fafc;
    position: fixed;
    top: 0;
    left: 0;
  }
  
  .title {
    font-size: 1.5rem;
    font-weight: bold;
  }
  
  .subtitle {
    margin-left: 1rem;
    font-size: 0.875rem;
    color: #a0aec0;
  }
  
  .settings {
    margin-left: auto;
    padding: 0.5rem 0.75rem;
    font-size: 0.875rem;
    cursor: pointer;
    border-radius: 0.375rem;
    transition: background-color 0.3s;
  }
  
  .settings:hover {
    background-color: white;
  }
  
  .chat-list {
    flex: 1;
    margin: 5rem 0.5rem 0.5rem;
    padding-bottom: 1rem;
    overflow-y: auto;
  }
  
  .chat-item {
    display: flex;
    flex-direction: column;
    padding: 0.75rem 1rem;
    border-radius: 0.5rem;
    transition: background-color 0.3s;
  }
  
  .chat-item:hover {
    background-color: #f1f5f9;
  }
  
  .chat-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
  }
  
  .role {
    font-weight: bold;
  }
  
  .copy-button {
    visibility: hidden;
  }
  
  .chat-item:hover .copy-button {
    visibility: visible;
  }
  
  .chat-content {
    display: flex;
    flex-direction: column;
  }
  
  .content-text {
    font-size: 0.875rem;
    color: #4a5568;
    line-height: 1.5;
  }
  
  .input-container {
    width: 100%;
    padding: 1.5rem;
    padding-bottom: 2rem;
    background-color: #f7fafc;
    position: sticky;
    bottom: 0;
  }
  
  .config-text {
    margin-top: -0.5rem;
    margin-bottom: 0.5rem;
    font-size: 0.875rem;
    color: #a0aec0;
  }
  
  .input-wrapper {
    display: flex;
    align-items: center;
  }
  
  .input {
    padding: 0.75rem 1rem;
    color: #4a5568;
    background-color: white;
    border: 1px solid #cbd5e0;
    border-radius: 0.375rem;
    margin-right: 0.5rem;
    flex-grow: 1;
    outline: none;
    transition: border-color 0.2s, box-shadow 0.2s;
  }
  
  .input:focus {
    border-color: #4299e1;
    box-shadow: 0 0 0 4px rgba(66, 153, 225, 0.4);
  }
  
  .button {
    padding: 0.75rem 1rem;
    font-size: 0.875rem;
    font-weight: 500;
    text-transform: capitalize;
    color: white;
    background-color: #2563eb;
    border-radius: 0.375rem;
    transition: background-color 0.3s;
    cursor: pointer;
  }
  
  .button:disabled {
    background-color: #a0aec0;
  }
  
  .button:hover {
    background-color: #2b6cb0;
  }
  
  .button:focus {
    outline: none;
    background-color: #2b6cb0;
  }
  
  pre {
    font-family: -apple-system, "Noto Sans", "Helvetica Neue", Helvetica,
      "Nimbus Sans L", Arial, "Liberation Sans", "PingFang SC", "Hiragino Sans GB",
      "Noto Sans CJK SC", "Source Han Sans SC", "Source Han Sans CN",
      "Microsoft YaHei", "Wenquanyi Micro Hei", "WenQuanYi Zen Hei", "ST Heiti",
      SimHei, "WenQuanYi Zen Hei Sharp", sans-serif;
  }
  </style>