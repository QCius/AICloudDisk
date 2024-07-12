package com.easypan.controller;

import com.easypan.entity.ChatCompleteResp;
import com.easypan.entity.ChatCompleteRespChoice;
import com.easypan.entity.Message;
import com.easypan.entity.constants.Constants;
import com.easypan.entity.vo.ResponseVO;
import com.easypan.entity.MoonShotClient;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import com.easypan.entity.Message;
import org.springframework.http.*;
import org.springframework.web.bind.annotation.*;


import javax.servlet.http.HttpSession;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

@RestController("AIController")
@RequestMapping("/AI")
public class AIController extends ABaseController {
    private static final String MOONSHOT_BASE_URL = "https://api.moonshot.cn/v1";
    private static final String SYSTEM_MESSAGE = "你是 网盘助手懒子哥,你更擅长中文和英文的对话。你会为用户提供安全,有帮助,准确的回答。Moonshot AI 为专有名词，不可翻译成其他语言。";

    MoonShotClient client = MoonShotClient.create("sk-j6n00tElc97ogd5bn93YlpuFulTpyUOTtilKOGFxo4WhOM7C");

    @RequestMapping("/chat")
    public ResponseVO aiChat(HttpSession session) {
        //String query=(String) session.getAttribute(Constants.GET_QUERY);
        String query="描述一下软件工程";
        String res;
        ChatCompleteResp response;
        response = client.chatComplete(SYSTEM_MESSAGE, query);
        if (response != null) {
            res = response.getChoices().get(0).getMessage().getContent();
        } else {
            res = "No response from AI";
        }
        return getSuccessResponseVO(res);
    }

    @RequestMapping("/fileconclude")
    public ResponseVO fileConclude(HttpSession session) {
        String res;
        String query="";
        ChatCompleteResp response;
        response = client.chatComplete(SYSTEM_MESSAGE, query);
        if (response != null) {
            res = response.getChoices().get(0).getMessage().getContent();
        } else {
            res = "No response from AI";
        }
        return getSuccessResponseVO(res);
    }
    @RequestMapping("/test")
    public String test() {
            return "test000";
        }

}

