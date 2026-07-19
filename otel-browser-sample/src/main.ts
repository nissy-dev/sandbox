import "./style.css";
import { logs } from "@opentelemetry/api-logs";
import { NavigationTimingInstrumentation } from "@opentelemetry/browser-instrumentation/experimental/navigation-timing";
import { UserActionInstrumentation } from "@opentelemetry/browser-instrumentation/experimental/user-action";
import { WebVitalsInstrumentation } from "@opentelemetry/browser-instrumentation/experimental/web-vitals";
import {
  createDefaultSessionIdGenerator,
  createLocalStorageSessionStore,
  createSessionLogRecordProcessor,
  createSessionManager,
  createSessionSpanProcessor,
} from "@opentelemetry/browser-sdk/session";
import { OTLPLogExporter } from "@opentelemetry/exporter-logs-otlp-http";
import { OTLPTraceExporter } from "@opentelemetry/exporter-trace-otlp-http";
import { registerInstrumentations } from "@opentelemetry/instrumentation";
import { FetchInstrumentation } from "@opentelemetry/instrumentation-fetch";
import { XMLHttpRequestInstrumentation } from "@opentelemetry/instrumentation-xml-http-request";
import { browserDetector } from "@opentelemetry/opentelemetry-browser-detector";
import {
  detectResources,
  resourceFromAttributes,
} from "@opentelemetry/resources";
import {
  ConsoleLogRecordExporter,
  LoggerProvider,
  SimpleLogRecordProcessor,
} from "@opentelemetry/sdk-logs";
import {
  ConsoleSpanExporter,
  SimpleSpanProcessor,
} from "@opentelemetry/sdk-trace";
import { WebTracerProvider } from "@opentelemetry/sdk-trace-web";
import { ATTR_SERVICE_NAME } from "@opentelemetry/semantic-conventions";

const OTLP_BASE_URL = "http://localhost:4318";
const OTLP_URL_PATTERN = /^http:\/\/localhost:4318\//;

async function initializeTelemetry() {
  // --- Resource detection ---
  let resource = resourceFromAttributes({
    [ATTR_SERVICE_NAME]: "otel-browser-with-tracing",
  });
  resource = resource.merge(
    detectResources({
      detectors: [browserDetector],
    }),
  );

  // --- Sessions ---
  // Session processors must run before export processors so session.id is
  // attached to each log record and span before export.
  const sessionManager = createSessionManager({
    sessionIdGenerator: createDefaultSessionIdGenerator(),
    sessionStore: createLocalStorageSessionStore(),
    maxDuration: 4 * 60 * 60,
    inactivityTimeout: 30 * 60,
  });
  await sessionManager.start();

  // --- Event-based instrumentations ---
  const logProvider = new LoggerProvider({
    resource,
    processors: [
      createSessionLogRecordProcessor(sessionManager),
      new SimpleLogRecordProcessor({
        exporter: new ConsoleLogRecordExporter(),
      }),
      new SimpleLogRecordProcessor({
        exporter: new OTLPLogExporter({
          url: `${OTLP_BASE_URL}/v1/logs`,
        }),
      }),
    ],
  });
  logs.setGlobalLoggerProvider(logProvider);

  // --- Span-based instrumentations ---
  const provider = new WebTracerProvider({
    resource,
    spanProcessors: [
      createSessionSpanProcessor(sessionManager),
      new SimpleSpanProcessor({ exporter: new ConsoleSpanExporter() }),
      new SimpleSpanProcessor({
        exporter: new OTLPTraceExporter({
          url: `${OTLP_BASE_URL}/v1/traces`,
        }),
      }),
    ],
  });
  provider.register();

  // --- Register all instrumentations ---
  registerInstrumentations({
    instrumentations: [
      // Event-based
      new NavigationTimingInstrumentation(),
      new UserActionInstrumentation(),
      new WebVitalsInstrumentation(),
      // Span-based. Exclude OTLP requests to prevent recursive telemetry.
      new FetchInstrumentation({
        ignoreUrls: [OTLP_URL_PATTERN],
      }),
      new XMLHttpRequestInstrumentation({
        ignoreUrls: [OTLP_URL_PATTERN],
      }),
    ],
  });

  // --- Button handlers ---
  document.getElementById("fetch-button")?.addEventListener("click", () => {
    void fetch("https://httpbin.org/get");
  });

  document.getElementById("xhr-button")?.addEventListener("click", () => {
    const xhr = new XMLHttpRequest();
    xhr.open("GET", "https://httpbin.org/get");
    xhr.send();
  });
}

void initializeTelemetry();
