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
  import { ref } from 'vue';
  import { chat } from '@/libs/gpt';
  import cryptoJS from "crypto-js";
  
  const summary = ref('');
  
  
  let apiKey = "sk-CzTkhkpuVlxFp2hE80E1D2B668554e35A71d9c16D6BfFdF5";
  
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