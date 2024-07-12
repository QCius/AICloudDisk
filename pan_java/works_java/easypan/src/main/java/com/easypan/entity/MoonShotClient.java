package com.easypan.entity;

import java.util.HashMap;
import java.util.Map;

import com.easypan.entity.constants.ApiUrls;
import com.easypan.entity.constants.Models;
import com.easypan.utils.*;
import static com.easypan.entity.constants.Constants.TEMPERATURE;

public class MoonShotClient {
    private final String baseUrl;
    private final String model;
    private final Map<String, String> authHeaders;
    private MoonShotClient(String model, String key, String baseUrl) {
        this.baseUrl = baseUrl;
        this.model = model;
        this.authHeaders = new HashMap<String, String>() {{
            put("Authorization", "Bearer " + key);
        }};
    }

    public static MoonShotClient create(String model, String key, String baseUrl) {
        return new MoonShotClient(model, key, baseUrl);
    }

    /**
     * 典型情况下使用本方法，使用默认的baseUrl
     *
     * @param key
     * @return
     */
    public static MoonShotClient create(String key) {
        return new MoonShotClient(Models.moonshot_v1_8k, key, ApiUrls.DEFAULT_BASE);
    }

    /**
     * 对话接口
     *
     * @param systemPrompt
     * @param userPrompt
     * @return
     */
    public ChatCompleteResp chatComplete(String systemPrompt, String userPrompt) {
        ChatCompleteReq dto = ChatCompleteReq.create(model, TEMPERATURE).addMessage(systemPrompt, userPrompt);
        return HttpUtil.requestJson(baseUrl + ApiUrls.CHAT_COMPLETE, "POST", dto, ChatCompleteResp.class, authHeaders);
    }
}