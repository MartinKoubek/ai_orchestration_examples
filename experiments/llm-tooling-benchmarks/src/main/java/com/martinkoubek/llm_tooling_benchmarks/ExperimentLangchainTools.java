package com.martinkoubek.llm_tooling_benchmarks;

import com.fasterxml.jackson.databind.ObjectMapper;
import dev.langchain4j.service.AiServices;
import dev.langchain4j.service.Result;
import dev.langchain4j.service.spring.AiService;
import dev.langchain4j.service.tool.ToolExecution;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.util.*;
import java.util.stream.Collectors;

@AiService
interface ExperimentalToolAssistant {
    Result<String> chat(String userMessage);
}

public class ExperimentLangchainTools {

    private static final Path TOOLS_JSON = resolveToolsJson();
    private static final ObjectMapper OBJECT_MAPPER = new ObjectMapper();
    private static String JSON_ID;
    private static String ENTRIES;
    private static String MERGE_SIZE;

    public static void main(String[] args) throws IOException {
        // 1) Load tools
        List<ToolItem> tools = loadTools();

        // 2) Run just the first configured model (keep your original 'break' behavior)
        for (ChatModelRegistry.NamedChatModel entry : ChatModelRegistry.getAllModels()) {
            runExperiment(entry, tools);
        }
    }

    private static List<ToolItem> loadTools() throws IOException {
        var jsonNode = OBJECT_MAPPER.readTree(Files.readString(TOOLS_JSON));
        var toolsNode = jsonNode.isArray() ? jsonNode : jsonNode.get("tools");
        if (toolsNode == null || !toolsNode.isArray()) {
            throw new IllegalStateException("tools_limited.json must contain an array under 'tools'.");
        }
        JSON_ID = String.valueOf(jsonNode.isArray() ? jsonNode : jsonNode.get("id"));
        ENTRIES = String.valueOf(jsonNode.isArray() ? jsonNode : jsonNode.get("entries"));
        MERGE_SIZE = String.valueOf(jsonNode.isArray() ? jsonNode : jsonNode.get("merge_size"));

        List<ToolItem> items = new ArrayList<>();
        for (var node : toolsNode) {
            var toolsArray = node.get("tools");
            if (toolsArray == null || !toolsArray.isArray() || toolsArray.isEmpty()) {
                throw new IllegalStateException("Each entry must include a non-empty 'tools' array.");
            }
            List<String> toolNames = new ArrayList<>();
            for (var toolNode : toolsArray) {
                String name = toolNode.asText();
                if (name == null || name.isBlank()) {
                    throw new IllegalStateException("Tool names must be non-empty strings.");
                }
                toolNames.add(name);
            }
            String prompt = node.path("prompt").asText();
            if (prompt == null || prompt.isBlank()) {
                throw new IllegalStateException("Each entry must include a prompt.");
            }
            items.add(new ToolItem(toMethodName(toolNames), List.copyOf(toolNames), prompt));
        }
        return items;
    }

    private static Path resolveToolsJson() {
        List<Path> candidates = List.of(
                Path.of("src/main/java/com/martinkoubek/llm_tooling_benchmarks/tools_limited.json"),
                Path.of("tools_limited.json")
        );
        return candidates.stream()
                .filter(Files::exists)
                .findFirst()
                .orElse(candidates.get(0));
    }

    private static void runExperiment(ChatModelRegistry.NamedChatModel entry,
                                      List<ToolItem> tools) throws IOException {
        System.out.println("\nModel: " + entry.name());
        Path dir = Path.of("src/main/java/com/martinkoubek/llm_tooling_benchmarks/data");

        if (!Files.exists(dir)) {
            Files.createDirectories(dir);  // creates all missing parent dirs too
            System.out.println("Directory created: " + dir);
        }


        var fileName = "model_" + entry.name() + "_size" + ENTRIES + "_merge" + MERGE_SIZE + "_id" + JSON_ID;
        Path logFile = dir.resolve(fileName + ".csv");
        Path summaryFile = dir.resolve(fileName + "_summary.json");

        Files.deleteIfExists(logFile);
        Files.deleteIfExists(summaryFile);

        Files.writeString(
                logFile,
                "\"tool_name;input_tokens;output_tokens;time_delta;tool_called;tool_not_called\n",
                StandardCharsets.UTF_8,
                StandardOpenOption.CREATE, StandardOpenOption.APPEND
        );

        long inputTokenSum = 0L;
        long outputTokenSum = 0L;
        double calledCount = 0;
        long timeDelta = 0;


        ExperimentalToolAssistant assistant = AiServices.builder(ExperimentalToolAssistant.class)
                .chatModel(entry.model())
                .tools(new Tools()) // your typed @Tool class
                .build();

        StringBuilder csv = new StringBuilder();
        csv.append("tool_name;input_tokens;output_tokens;time_delta;tool_called;tool_not_called\n");

        for (ToolItem t : tools) {
            System.out.println("→ " + t.methodName() + " (" + String.join(", ", t.toolNames()) + ")");

            long start = System.currentTimeMillis();
            Result<String> res = assistant.chat(
                    "You are autonomous tool assistant that executes tools without requiring additional questions. " +
                                "If some additional information is requested, create them for demo purposes.\n\n" +
                                t.prompt());
            long timeD = System.currentTimeMillis() - start;
            timeDelta += timeD;

            int inputTokens = (res.tokenUsage() == null) ? 0 : res.tokenUsage().inputTokenCount();
            int outputTokens = (res.tokenUsage() == null) ? 0 : res.tokenUsage().outputTokenCount();
            ToolMatchReport toolCalled = summarizeToolResults(res.toolExecutions(), t, res);

            inputTokenSum += inputTokens;
            outputTokenSum += outputTokens;
            calledCount += toolCalled.percent();

            String line = escapeCsv(t.methodName()) + ";" + inputTokens + ";" + outputTokens + ";" + timeDelta + ";" +
                    toolCalled.percent() + ";" + toolCalled.matched() + ";" + toolCalled.unmatched() + ";" + toolCalled.executions() + ";\n";
            System.out.println("\t" + line);

            Files.writeString(
                    logFile,
                    line,
                    StandardCharsets.UTF_8,
                    StandardOpenOption.CREATE, StandardOpenOption.APPEND
            );
        }
        System.out.println("CSV appended to: " + logFile.toAbsolutePath());

        // --- Build summary JSON payload ---
        double avgInputTokens = (tools.size() == 0) ? 0.0 : ((double) inputTokenSum) / tools.size();
        double avgOutputTokens = (tools.size() == 0) ? 0.0 : ((double) outputTokenSum) / tools.size();
        double avgCalledPct = (tools.size() == 0) ? 0.0 : ((double) calledCount / tools.size());
        double avgTimeDelta = (tools.size() == 0) ? 0.0 : ((double) timeDelta / tools.size());


        // Create a simple Map for JSON serialization
        var summary = new java.util.LinkedHashMap<String, Object>();
        summary.put("model name", entry.name());
        summary.put("avg_input_tokens", avgInputTokens);
        summary.put("avg_output_tokens", avgOutputTokens);
        summary.put("avg_tools_called", avgCalledPct);
        summary.put("avg_time", avgTimeDelta);

        // Write JSON (pretty) into *_summary.csv (per your request)
        String json = OBJECT_MAPPER.writerWithDefaultPrettyPrinter().writeValueAsString(summary);
        Files.writeString(
                summaryFile,
                json + "\n",
                StandardCharsets.UTF_8,
                StandardOpenOption.CREATE, StandardOpenOption.TRUNCATE_EXISTING
        );
        System.out.println("Summary written: " + summaryFile.toAbsolutePath());
    }

    public record ToolMatchReport(int percent,
                                  List<String> matched,
                                  List<String> unmatched,
                                  String executions) {}

    private static ToolMatchReport summarizeToolResults(
            List<ToolExecution> executions, ToolItem tool, Result<String> res) {

        List<String> expectedNames = tool.toolNames().stream()
            .map(name -> name.toLowerCase(Locale.ROOT))
            .collect(Collectors.toList());

        if (executions == null || executions.isEmpty() || expectedNames == null || expectedNames.isEmpty()) {
            return new ToolMatchReport(0, List.of(), expectedNames == null ? List.of() : List.copyOf(expectedNames), "Executions are empty or tools were not called: " + res.finalResponse().toString());
        }

        // Precompute lowercase result blobs for fast contains checks
        List<String> lowerResults = executions.stream()
                .map(ex -> ex == null || ex.result() == null ? "" : ex.result().toLowerCase(Locale.ROOT))
                .toList();

        // Build matched list using case-insensitive contains against any result
        List<String> matched = expectedNames.stream()
                .filter(Objects::nonNull)
                .filter(name -> {
                    String needle = name.toLowerCase(Locale.ROOT);
                    return lowerResults.stream().anyMatch(r -> r.contains(needle));
                })
                .collect(Collectors.toList());

        // Unmatched = expected - matched (preserve original casing/order from expectedNames)
        Set<String> matchedSet = new HashSet<>(matched);
        List<String> unmatched = expectedNames.stream()
                .filter(Objects::nonNull)
                .filter(name -> !matchedSet.contains(name))
                .collect(Collectors.toList());

        long count = matched.size();
        int percent = (int) Math.round((count / (double) expectedNames.size()) * 100.0);
        if (unmatched.size() > 0){
            System.out.println("\t\tTool was not called: " + executions);
        }

        return new ToolMatchReport(percent, matched, unmatched, executions.toString());
    }


    private static String escapeCsv(String value) {
        String safe = (value == null) ? "" : value.replace("\"", "\"\"");
        return "\"" + safe + "\"";
    }

    private static String toMethodName(List<String> toolNames) {
        String combined = String.join("_", toolNames);
        StringBuilder builder = new StringBuilder();
        boolean capitalizeNext = false;
        for (int i = 0; i < combined.length(); i++) {
            char c = combined.charAt(i);
            if (!Character.isLetterOrDigit(c)) {
                capitalizeNext = true;
                continue;
            }
            if (builder.length() == 0) {
                builder.append(Character.toLowerCase(c));
                capitalizeNext = false;
                continue;
            }
            if (capitalizeNext) {
                builder.append(Character.toUpperCase(c));
                capitalizeNext = false;
            } else {
                builder.append(c);
            }
        }
        return builder.toString();
    }

    public record ToolItem(String methodName, List<String> toolNames, String prompt) {
        public ToolItem {
            Objects.requireNonNull(methodName, "methodName");
            Objects.requireNonNull(toolNames, "toolNames");
            Objects.requireNonNull(prompt, "prompt");
            if (toolNames.isEmpty()) {
                throw new IllegalArgumentException("toolNames must not be empty");
            }
        }
    }
}
