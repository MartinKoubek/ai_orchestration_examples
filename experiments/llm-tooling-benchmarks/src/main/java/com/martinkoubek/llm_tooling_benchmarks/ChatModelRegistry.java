package com.martinkoubek.llm_tooling_benchmarks;

import dev.langchain4j.data.message.AiMessage;
import dev.langchain4j.data.message.ChatMessage;
import dev.langchain4j.data.message.UserMessage;
import dev.langchain4j.model.chat.ChatModel;
import dev.langchain4j.model.chat.response.ChatResponse;
import dev.langchain4j.model.output.TokenUsage;

import java.util.List;
import java.util.Locale;
import java.util.stream.Collectors;

/**
 * Provides a small catalog of in-memory {@link ChatModel} implementations so experiments
 * can run without depending on external model providers.
 */
public final class ChatModelRegistry {

    public record NamedChatModel(String name, ChatModel model) {}

    private static final List<NamedChatModel> MODELS = List.of(
            register("martinkoubek-mini"),
            register("martinkoubek-standard"),
            register("martinkoubek-pro")
    );

    private ChatModelRegistry() {
    }

    public static Iterable<NamedChatModel> getAllModels() {
        return MODELS;
    }

    private static NamedChatModel register(String name) {
        return new NamedChatModel(name, new LocalChatModel(name));
    }

    private static final class LocalChatModel implements ChatModel {

        private final String modelName;

        private LocalChatModel(String modelName) {
            this.modelName = modelName;
        }

        @Override
        public ChatResponse chat(List<ChatMessage> messages) {
            String userInstructions = messages == null
                    ? ""
                    : messages.stream()
                            .filter(msg -> msg instanceof UserMessage)
                            .map(UserMessage.class::cast)
                            .map(LocalChatModel::textFromUserMessage)
                            .filter(text -> text != null && !text.isBlank())
                            .collect(Collectors.joining(" | "));

            if (userInstructions.isBlank()) {
                userInstructions = "No user instructions provided.";
            }

            String reply = "[%s] %s".formatted(
                    modelName.toUpperCase(Locale.ROOT),
                    summarize(userInstructions)
            );

            AiMessage aiMessage = AiMessage.from(reply);
            TokenUsage usage = new TokenUsage(
                    userInstructions.length(),
                    reply.length(),
                    userInstructions.length() + reply.length()
            );

            return ChatResponse.builder()
                    .aiMessage(aiMessage)
                    .modelName(modelName)
                    .tokenUsage(usage)
                    .build();
        }

        private static String summarize(String text) {
            if (text.length() <= 200) {
                return text;
            }
            return text.substring(0, 200) + " …";
        }

        private static String textFromUserMessage(UserMessage message) {
            if (message == null) {
                return null;
            }
            if (message.hasSingleText()) {
                return message.singleText();
            }
            return message.toString();
        }
    }
}
