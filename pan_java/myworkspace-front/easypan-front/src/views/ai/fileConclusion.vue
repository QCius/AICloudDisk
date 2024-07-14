<template>
  <div class="container">
    <div class="header">
      <div class="title">文件上传及总结生成器</div>
    </div>

    <div class="upload-container">
      <input type="file" @change="handleFileUpload" />
    </div>

    <div class="result-container">
      <textarea v-model="summary" placeholder="文件总结将在这里显示..." readonly></textarea>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref,watch } from 'vue';
import { chat } from '@/libs/gpt';
import cryptoJS from "crypto-js";
import type { ChatMessage } from "@/types";

const summary = ref('');
let apiKey = "sk-CzTkhkpuVlxFp2hE80E1D2B668554e35A71d9c16D6BfFdF5";
const decoder = new TextDecoder("utf-8");

const clearSummary = () => {
  summary.value = '';
};
const messageList=ref<ChatMessage[]>()
const handleFileUpload = async (event: Event) => {
  const file = (event.target as HTMLInputElement).files?.[0];
  if (!file) {
    return;
  }

  try {
    clearSummary();
    const fileContent = await file.text();
    messageList.value = [{role: 'user', content: `请对以下文档内容进行总结：\n\n${fileContent}`}];
    messageList.value.push({role: 'assistant', content: '正在生成总结，请稍候...'});
    const { body, status } = await chat(messageList.value, getAPIKey());
    console.log(body, status);
    if (body) {
      const reader = body.getReader();
      await readStream(reader, status);
    }
  } catch (error) {
    summary.value = `发生错误：${error.message}`;
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
      summary.value+=content;
      appendLastMessageContent(content);
    }
  }
};
const appendLastMessageContent = (content: string) =>
  (messageList.value[messageList.value.length - 1].content += content);


const getAPIKey = () => {
  if (apiKey) return apiKey;
  const aesAPIKey = localStorage.getItem("apiKey") ?? "";
  apiKey = cryptoJS.AES.decrypt(aesAPIKey, getSecretKey()).toString(
    cryptoJS.enc.Utf8
  );
  return apiKey;
};

const getSecretKey = () => 'lianginx';
</script>

<style scoped>
.container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  padding: 1rem;
}

.header {
  display: flex;
  justify-content: center;
  width: 100%;
  padding: 1rem 1.5rem;
  background-color: #f7fafc;
  margin-bottom: 1rem;
}

.title {
  font-size: 1.5rem;
  font-weight: bold;
}

.upload-container {
  text-align: center;
  margin-bottom: 1.5rem;
}

.upload-container input[type="file"] {
  padding: 0.5rem;
  border: 1px solid #cbd5e0;
  border-radius: 0.375rem;
  outline: none;
}

.result-container {
  flex: 1;
  display: flex;
  justify-content: center;
}

.result-container textarea {
  width: 100%;
  height: 100%;
  padding: 1rem;
  color: #4a5568;
  background-color: white;
  border: 1px solid #cbd5e0;
  border-radius: 0.375rem;
  resize: none;
  outline: none;
  font-size: 0.875rem;
}
</style>