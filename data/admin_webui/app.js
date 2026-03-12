import React, { useEffect, useState } from "https://esm.sh/react@18.3.1";
import { createRoot } from "https://esm.sh/react-dom@18.3.1/client";
import htm from "https://esm.sh/htm@3.1.1";
import {
  ThemeProvider,
  alpha,
  createTheme,
} from "https://esm.sh/@mui/material@5.16.14/styles?deps=react@18.3.1";
import {
  Alert,
  AppBar,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Container,
  CssBaseline,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Drawer,
  FormControlLabel,
  IconButton,
  LinearProgress,
  List,
  ListItemButton,
  ListItemText,
  MenuItem,
  Snackbar,
  Stack,
  Switch,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Toolbar,
  Typography,
  useMediaQuery,
} from "https://esm.sh/@mui/material@5.16.14?deps=react@18.3.1";

const html = htm.bind(React.createElement);

const NAV_ITEMS = [
  { key: "dashboard", label: "总览", eyebrow: "Overview" },
  { key: "subscriptions", label: "订阅中心", eyebrow: "Subscriptions" },
  { key: "items", label: "商品中心", eyebrow: "Items" },
  { key: "runtime", label: "运行状态", eyebrow: "Runtime" },
  { key: "config", label: "配置中心", eyebrow: "Config" },
];

const UI = {
  radiusShell: "var(--radius-shell)",
  radiusSurface: "var(--radius-surface)",
  radiusControl: "var(--radius-control)",
  spacingPage: 4,
  spacingSection: 3,
  spacingCompact: 2,
  cardPadding: { xs: 3, md: 4 },
};

const theme = createTheme({
  palette: {
    mode: "light",
    primary: { main: "#2563eb" },
    secondary: { main: "#f97316" },
    success: { main: "#059669" },
    warning: { main: "#d97706" },
    error: { main: "#dc2626" },
    background: {
      default: "#eff6ff",
      paper: "rgba(255, 255, 255, 0.62)",
    },
    text: {
      primary: "#10243e",
      secondary: "#52637a",
    },
  },
  shape: { borderRadius: 28 },
  typography: {
    fontFamily: "'Segoe UI Variable', 'PingFang SC', 'Noto Sans SC', sans-serif",
    h3: { fontWeight: 800, letterSpacing: "-0.04em" },
    h4: { fontWeight: 780, letterSpacing: "-0.03em" },
    h5: { fontWeight: 760, letterSpacing: "-0.02em" },
    h6: { fontWeight: 720 },
    button: { textTransform: "none", fontWeight: 700 },
  },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          minHeight: "100vh",
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          borderRadius: UI.radiusSurface,
          background: "rgba(255, 255, 255, 0.52)",
          color: "#10243e",
          border: "1px solid rgba(255, 255, 255, 0.45)",
          backdropFilter: "blur(18px)",
          boxShadow: "0 24px 48px rgba(15, 23, 42, 0.08)",
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: UI.radiusSurface,
          border: "1px solid rgba(255, 255, 255, 0.42)",
          background: "rgba(255, 255, 255, 0.56)",
          backdropFilter: "blur(22px)",
          boxShadow: "0 24px 50px rgba(30, 41, 59, 0.08)",
        },
      },
    },
    MuiDrawer: {
      styleOverrides: {
        paper: {
          borderRadius: UI.radiusShell,
          background: "rgba(247, 250, 255, 0.72)",
          backdropFilter: "blur(24px)",
          borderRight: "1px solid rgba(255, 255, 255, 0.48)",
        },
      },
    },
    MuiDialog: {
      styleOverrides: {
        paper: {
          borderRadius: UI.radiusSurface,
          background: "rgba(248, 251, 255, 0.8)",
          backdropFilter: "blur(24px)",
          border: "1px solid rgba(255, 255, 255, 0.48)",
          boxShadow: "0 32px 70px rgba(15, 23, 42, 0.16)",
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: UI.radiusControl,
          paddingInline: 16,
          minHeight: 40,
        },
        contained: {
          backgroundImage: "linear-gradient(135deg, #2563eb, #0ea5e9)",
          boxShadow: "0 18px 32px rgba(37, 99, 235, 0.24)",
        },
        outlined: {
          borderColor: "rgba(37, 99, 235, 0.18)",
          background: "rgba(255, 255, 255, 0.42)",
        },
        text: {
          color: "#1d4ed8",
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: 999,
          fontWeight: 700,
          backdropFilter: "blur(14px)",
        },
      },
    },
    MuiTableCell: {
      styleOverrides: {
        root: {
          borderBottom: "1px solid rgba(148, 163, 184, 0.16)",
          verticalAlign: "middle",
        },
        head: {
          color: "#61728a",
          fontWeight: 700,
        },
      },
    },
    MuiTableContainer: {
      styleOverrides: {
        root: {
          borderRadius: UI.radiusSurface,
        },
      },
    },
    MuiCardContent: {
      styleOverrides: {
        root: {
          position: "relative",
          zIndex: 1,
        },
      },
    },
    MuiOutlinedInput: {
      styleOverrides: {
        root: {
          borderRadius: UI.radiusControl,
          background: "rgba(255, 255, 255, 0.5)",
          backdropFilter: "blur(10px)",
        },
      },
    },
  },
});

function getRoute() {
  const route = window.location.hash.replace(/^#\/?/, "").trim();
  return NAV_ITEMS.some((item) => item.key === route) ? route : "dashboard";
}

function setRoute(route) {
  window.location.hash = `#/${route}`;
}

function formatTs(value) {
  if (!value) return "-";
  return new Date(value * 1000).toLocaleString("zh-CN", { hour12: false });
}

function formatMoney(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return "-";
  }
  return `¥${Number(value).toFixed(2)}`;
}

function toNumberOrNull(value) {
  if (value === "" || value === null || value === undefined) {
    return null;
  }
  const next = Number(value);
  return Number.isFinite(next) ? next : null;
}

async function api(path, options = {}) {
  const config = {
    method: options.method || "GET",
    credentials: "include",
    headers: {},
  };
  if (options.body !== undefined) {
    config.headers["Content-Type"] = "application/json";
    config.body = JSON.stringify(options.body);
  }

  const response = await fetch(path, config);
  const contentType = response.headers.get("content-type") || "";
  const payload = contentType.includes("application/json") ? await response.json() : {};

  if (response.status === 401) {
    const error = new Error("需要重新登录");
    error.code = "UNAUTHORIZED";
    throw error;
  }
  if (!response.ok || payload.ok === false) {
    const error = new Error(payload?.error?.message || `请求失败: ${response.status}`);
    error.payload = payload;
    throw error;
  }
  return payload;
}

function statusChipProps(enabled, pausedReason) {
  if (enabled) {
    return { label: "启用中", color: "success", variant: "filled" };
  }
  return { label: pausedReason || "已暂停", color: "warning", variant: "outlined" };
}

function SectionHeader({ eyebrow, title, description, action }) {
  return html`
    <${Stack}
      direction=${{ xs: "column", md: "row" }}
      spacing=${2}
      justifyContent="space-between"
      alignItems=${{ xs: "flex-start", md: "center" }}
    >
      <${Box}>
        ${eyebrow ? html`<${Typography} variant="overline" color="primary.main">${eyebrow}<//>` : null}
        <${Typography} variant="h5" sx=${{ mt: eyebrow ? 0.25 : 0 }}>${title}<//>
        ${description
          ? html`<${Typography} variant="body2" color="text.secondary" sx=${{ mt: 0.75 }}>
              ${description}
            <//>`
          : null}
      <//>
      ${action || null}
    <//>
  `;
}

function MetricCard({ title, value, caption, tone = "primary" }) {
  return html`
    <${Card} className="glass-card metric-glow" elevation=${0}>
      <${CardContent} sx=${{ p: UI.cardPadding }}>
        <${Stack} spacing=${UI.spacingCompact}>
          <${Typography} variant="overline" color="text.secondary">${title}<//>
          <${Typography}
            variant="h4"
            sx=${{
              color: tone === "secondary" ? "secondary.main" : tone === "success" ? "success.main" : "text.primary",
            }}
          >
            ${value}
          <//>
          <${Typography} variant="body2" color="text.secondary">${caption}<//>
        <//>
      <//>
    <//>
  `;
}

function JsonPanel({ title, description, value }) {
  return html`
    <${Card} className="glass-panel" elevation=${0}>
      <${CardContent} sx=${{ p: UI.cardPadding }}>
        <${Stack} spacing=${1.5}>
          <${Box}>
            <${Typography} variant="h6">${title}<//>
            ${description ? html`<${Typography} variant="body2" color="text.secondary">${description}<//>` : null}
          <//>
          <${Box}
            sx=${{
              borderRadius: UI.radiusControl,
              p: 2,
              bgcolor: alpha("#ffffff", 0.42),
              border: "1px solid rgba(255,255,255,0.42)",
            }}
          >
            <pre className="json-pre">${JSON.stringify(value, null, 2)}</pre>
          <//>
        <//>
      <//>
    <//>
  `;
}

function LoginView({ loading, error, onLogin }) {
  const [apiKey, setApiKey] = useState("");

  return html`
    <${Box}
      className="login-shell shell-bg"
      sx=${{
        display: "grid",
        placeItems: "center",
        px: 2,
        py: 6,
      }}
    >
      <${Card}
        className="glass-card"
        elevation=${0}
        sx=${{
          width: "min(520px, 100%)",
          borderRadius: UI.radiusShell,
        }}
      >
        <${CardContent} sx=${{ p: UI.cardPadding }}>
          <${Stack} spacing=${UI.spacingPage}>
            <${Box}>
              <${Box} className="hero-chip">Goofish Catcher Console<//>
              <${Typography} variant="h3" sx=${{ mt: 2 }}>闲鱼监控管理后台<//>
              <${Typography} variant="body1" color="text.secondary" sx=${{ mt: 1.25, maxWidth: 420 }}>
                使用管理员 API Key 登录本地控制台。后台默认仅监听 127.0.0.1，适合插件内嵌管理场景。
              <//>
            <//>
            ${error ? html`<${Alert} severity="error" variant="filled">${error}<//>` : null}
            <${TextField}
              label="管理员 API Key"
              type="password"
              value=${apiKey}
              onChange=${(event) => setApiKey(event.target.value)}
              onKeyDown=${(event) => {
                if (event.key === "Enter" && apiKey.trim()) {
                  onLogin(apiKey.trim());
                }
              }}
              fullWidth=${true}
            />
            <${Button}
              variant="contained"
              size="large"
              disabled=${loading || !apiKey.trim()}
              onClick=${() => onLogin(apiKey.trim())}
            >
              ${loading ? "登录中..." : "进入控制台"}
            <//>
          <//>
        <//>
      <//>
    <//>
  `;
}

function SubscriptionDialog({ open, value, onClose, onSubmit }) {
  const [form, setForm] = useState(value || {});

  useEffect(() => {
    setForm(value || {});
  }, [value, open]);

  const fields = [
    ["umo", "会话来源 UMO", "text"],
    ["keyword", "关键词", "text"],
    ["interval_sec", "轮询间隔（秒）", "number"],
    ["pages", "抓取页数", "number"],
    ["drop_abs", "绝对降价阈值", "number"],
    ["drop_pct", "相对降价阈值", "number"],
    ["new_window_sec", "上新窗口（秒）", "number"],
    ["cooldown_sec", "通知冷却（秒）", "number"],
  ];

  return html`
    <${Dialog}
      open=${open}
      onClose=${onClose}
      fullWidth=${true}
      maxWidth="sm"
      PaperProps=${{ className: "glass-dialog" }}
    >
      <${DialogTitle}>${value?.id ? "编辑订阅" : "新建订阅"}<//>
      <${DialogContent}>
        <${Stack} spacing=${2} sx=${{ mt: 1 }}>
          ${fields.map(([key, label, type]) => html`
            <${TextField}
              key=${key}
              label=${label}
              type=${type}
              value=${form[key] ?? ""}
              onChange=${(event) => setForm((current) => ({ ...current, [key]: event.target.value }))}
              fullWidth=${true}
            />
          `)}
        <//>
      <//>
      <${DialogActions} sx=${{ px: 3, pb: 3 }}>
        <${Button} onClick=${onClose}>取消<//>
        <${Button} variant="contained" onClick=${() => onSubmit(form)}>保存<//>
      <//>
    <//>
  `;
}

function DashboardPage({ notify }) {
  const [overview, setOverview] = useState(null);
  const [query, setQuery] = useState({ keyword: "", pages: 1 });
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(true);

  async function load() {
    try {
      setOverview(await api("/api/overview"));
    } catch (error) {
      notify(error.message, "error");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    const timer = window.setInterval(load, 8000);
    return () => window.clearInterval(timer);
  }, []);

  async function runQuery() {
    try {
      const payload = await api("/api/query", {
        method: "POST",
        body: {
          keyword: query.keyword,
          pages: Number(query.pages || 1),
        },
      });
      setPreview(payload.preview);
      notify("快速查询已完成", "success");
    } catch (error) {
      notify(error.message, "error");
    }
  }

  if (loading && !overview) {
    return html`
      <${Box} sx=${{ display: "grid", placeItems: "center", py: 12 }}>
        <${CircularProgress} />
      <//>
    `;
  }

  return html`
    <${Stack} spacing=${UI.spacingPage} className="page-enter">
      <${Card} className="glass-card dashboard-hero" elevation=${0}>
        <${CardContent} className="hero-surface" sx=${{ p: UI.cardPadding }}>
          <${Stack} spacing=${UI.spacingPage}>
            <${Box}>
              <${Box} className="hero-chip">Command Surface<//>
              <${Typography} variant="h4" sx=${{ mt: 2 }}>全局状态与快速查询<//>
              <${Typography} variant="body1" color="text.secondary" sx=${{ mt: 1.25, maxWidth: 720 }}>
                首页只保留运行决策最有价值的信息：Provider 模式、订阅规模、抓取成功率、队列状态，以及一键临时查询入口。
              <//>
            <//>
            <${Stack} direction=${{ xs: "column", md: "row" }} spacing=${UI.spacingCompact} flexWrap="wrap">
              <${Chip} label=${`Provider: ${overview?.provider_mode || "-"}`} color="primary" />
              <${Chip}
                label=${overview?.provider_available ? "Provider 可用" : "Provider 异常"}
                color=${overview?.provider_available ? "success" : "warning"}
                variant=${overview?.provider_available ? "filled" : "outlined"}
              />
              <${Chip}
                label=${overview?.scheduler_running ? "调度器运行中" : "调度器未运行"}
                color=${overview?.scheduler_running ? "success" : "warning"}
                variant=${overview?.scheduler_running ? "filled" : "outlined"}
              />
            <//>
          <//>
        <//>
      <//>

      <${Box} className="hero-grid">
        <${MetricCard}
          title="订阅总览"
          value=${`${overview?.enabled_subscriptions || 0}/${overview?.total_subscriptions || 0}`}
          caption=${`启用 ${overview?.enabled_subscriptions || 0}，暂停 ${overview?.paused_subscriptions || 0}`}
        />
        <${MetricCard}
          title="24h 抓取成功率"
          value=${`${Number(overview?.success_rate_24h || 0).toFixed(1)}%`}
          caption=${`成功 ${overview?.success_runs_24h || 0}，失败 ${overview?.failed_runs_24h || 0}`}
          tone="secondary"
        />
        <${MetricCard}
          title="队列 / 执行中"
          value=${`${overview?.queue_size || 0}/${overview?.inflight || 0}`}
          caption=${`Workers ${overview?.workers || 0}`}
        />
        <${MetricCard}
          title="最近告警"
          value=${overview?.recent_alerts?.length || 0}
          caption="展示最近异常与高价值事件摘要"
          tone="success"
        />
      <//>

      <${Box} className="surface-grid cols-2">
        <${Card} className="glass-card" elevation=${0}>
          <${CardContent} className="page-surface" sx=${{ p: UI.cardPadding }}>
            <${SectionHeader}
              eyebrow="Quick Query"
              title="临时查询"
              description="不创建订阅，直接跑一轮推荐分析。"
            />
            <${Stack} direction=${{ xs: "column", md: "row" }} spacing=${2} sx=${{ mt: UI.spacingSection }}>
              <${TextField}
                label="关键词"
                value=${query.keyword}
                onChange=${(event) => setQuery((current) => ({ ...current, keyword: event.target.value }))}
                fullWidth=${true}
              />
              <${TextField}
                label="页数"
                type="number"
                value=${query.pages}
                onChange=${(event) => setQuery((current) => ({ ...current, pages: event.target.value }))}
                sx=${{ width: { xs: "100%", md: 120 } }}
              />
              <${Button} variant="contained" onClick=${runQuery} disabled=${!query.keyword.trim()}>
                开始分析
              <//>
            <//>
            ${preview
              ? html`<${Box} sx=${{ mt: UI.spacingSection }}>
                  <${JsonPanel}
                    title="查询结果"
                    description="展示推荐结果、分析模式与回退原因。"
                    value=${preview}
                  />
                <//>`
              : null}
          <//>
        <//>

        <${Stack} spacing=${2}>
          <${JsonPanel}
            title="最近告警"
            description="来自运行层和业务层的最近信号。"
            value=${overview?.recent_alerts || []}
          />
          <${JsonPanel}
            title="24h / 7d 趋势"
            description="用于快速判断上新与降价变化。"
            value=${overview?.trends || []}
          />
        <//>
      <//>
    <//>
  `;
}

function SubscriptionsPage({ notify }) {
  const [filters, setFilters] = useState({ keyword: "", umo: "", status: "all" });
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [preview, setPreview] = useState(null);

  async function load() {
    try {
      const params = new URLSearchParams(filters);
      const payload = await api(`/api/subscriptions?${params.toString()}`);
      setItems(payload.items || []);
    } catch (error) {
      notify(error.message, "error");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, [filters.keyword, filters.umo, filters.status]);

  async function save(form) {
    const body = {
      ...form,
      interval_sec: toNumberOrNull(form.interval_sec),
      pages: toNumberOrNull(form.pages),
      drop_abs: toNumberOrNull(form.drop_abs),
      drop_pct: toNumberOrNull(form.drop_pct),
      new_window_sec: toNumberOrNull(form.new_window_sec),
      cooldown_sec: toNumberOrNull(form.cooldown_sec),
    };
    try {
      if (editing?.id) {
        await api(`/api/subscriptions/${editing.id}`, { method: "PATCH", body });
      } else {
        await api("/api/subscriptions", { method: "POST", body });
      }
      notify("订阅已保存", "success");
      setDialogOpen(false);
      setEditing(null);
      load();
    } catch (error) {
      notify(error.message, "error");
    }
  }

  async function runAction(id, action) {
    try {
      const payload = await api(`/api/subscriptions/${id}/${action}`, { method: "POST" });
      if (action === "check") {
        setPreview(payload.recommendation);
      }
      notify("操作成功", "success");
      load();
    } catch (error) {
      notify(error.message, "error");
    }
  }

  async function remove(id) {
    if (!window.confirm("确认删除这条订阅？")) {
      return;
    }
    try {
      await api(`/api/subscriptions/${id}`, { method: "DELETE" });
      notify("订阅已删除", "success");
      load();
    } catch (error) {
      notify(error.message, "error");
    }
  }

  return html`
    <${Stack} spacing=${UI.spacingPage} className="page-enter">
      <${Card} className="glass-card" elevation=${0}>
        <${CardContent} className="page-surface" sx=${{ p: UI.cardPadding }}>
          <${SectionHeader}
            eyebrow="Subscription Center"
            title="订阅中心"
            description="按关键词、会话来源和状态筛选，并直接执行暂停、恢复、立即检查。"
            action=${html`
              <${Button}
                variant="contained"
                onClick=${() => {
                  setEditing({
                    interval_sec: 600,
                    pages: 1,
                    drop_abs: 50,
                    drop_pct: 0.05,
                    new_window_sec: 1800,
                    cooldown_sec: 21600,
                  });
                  setDialogOpen(true);
                }}
              >
                新建订阅
              <//>
            `}
          />
          <${Stack} direction=${{ xs: "column", md: "row" }} spacing=${2} sx=${{ mt: UI.spacingSection }}>
            <${TextField}
              label="关键词"
              value=${filters.keyword}
              onChange=${(event) => setFilters((current) => ({ ...current, keyword: event.target.value }))}
              fullWidth=${true}
            />
            <${TextField}
              label="UMO"
              value=${filters.umo}
              onChange=${(event) => setFilters((current) => ({ ...current, umo: event.target.value }))}
              fullWidth=${true}
            />
            <${TextField}
              select=${true}
              label="状态"
              value=${filters.status}
              onChange=${(event) => setFilters((current) => ({ ...current, status: event.target.value }))}
              sx=${{ width: { xs: "100%", md: 160 } }}
            >
              <${MenuItem} value="all">全部<//>
              <${MenuItem} value="enabled">启用<//>
              <${MenuItem} value="paused">暂停<//>
            <//>
          <//>
        <//>
      <//>

      <${Card} className="glass-table" elevation=${0}>
        <${CardContent} className="page-surface" sx=${{ p: UI.cardPadding }}>
          ${loading ? html`<${LinearProgress} sx=${{ mb: 2 }} />` : null}
          <${TableContainer} className="table-relaxed">
            <${Table} size="small">
              <${TableHead}>
                <${TableRow}>
                  <${TableCell}>关键词<//>
                  <${TableCell}>UMO<//>
                  <${TableCell}>状态<//>
                  <${TableCell}>页数 / 间隔<//>
                  <${TableCell}>上次 / 下次<//>
                  <${TableCell}>失败次数<//>
                  <${TableCell} align="right">操作<//>
                <//>
              <//>
              <${TableBody}>
                ${items.map((item) => {
                  const chip = statusChipProps(item.enabled, item.paused_reason);
                  return html`
                    <${TableRow} key=${item.id} hover=${true}>
                      <${TableCell}>
                        <${Typography} variant="subtitle2">${item.keyword}<//>
                      <//>
                      <${TableCell}>${item.umo}<//>
                      <${TableCell}>
                        <${Chip}
                          size="small"
                          label=${chip.label}
                          color=${chip.color}
                          variant=${chip.variant}
                        />
                      <//>
                      <${TableCell}>${item.pages} / ${item.interval_sec}s<//>
                      <${TableCell}>
                        <${Stack} spacing=${0.5}>
                          <${Typography} variant="caption">${formatTs(item.last_run_at)}<//>
                          <${Typography} variant="caption" color="text.secondary">${formatTs(item.next_run_at)}<//>
                        <//>
                      <//>
                      <${TableCell}>${item.consecutive_failures}<//>
                      <${TableCell} align="right">
                        <${Stack} direction="row" spacing=${1} justifyContent="flex-end" flexWrap="wrap">
                          <${Button} size="small" onClick=${() => { setEditing(item); setDialogOpen(true); }}>编辑<//>
                          <${Button} size="small" onClick=${() => runAction(item.id, item.enabled ? "pause" : "resume")}>
                            ${item.enabled ? "暂停" : "恢复"}
                          <//>
                          <${Button} size="small" onClick=${() => runAction(item.id, "check")}>立即检查<//>
                          <${Button} size="small" color="error" onClick=${() => remove(item.id)}>删除<//>
                        <//>
                      <//>
                    <//>
                  `;
                })}
              <//>
            <//>
          <//>
        <//>
      <//>

      ${preview
        ? html`<${JsonPanel}
            title="最近一次检查结果"
            description="展示该订阅的即时推荐输出。"
            value=${preview}
          />`
        : null}

      <${SubscriptionDialog}
        open=${dialogOpen}
        value=${editing}
        onClose=${() => {
          setDialogOpen(false);
          setEditing(null);
        }}
        onSubmit=${save}
      />
    <//>
  `;
}

function ItemsPage({ notify }) {
  const [search, setSearch] = useState("");
  const [items, setItems] = useState([]);
  const [detail, setDetail] = useState(null);
  const [drawerOpen, setDrawerOpen] = useState(false);

  async function load() {
    try {
      const payload = await api(`/api/items?search=${encodeURIComponent(search)}`);
      setItems(payload.items || []);
    } catch (error) {
      notify(error.message, "error");
    }
  }

  useEffect(() => {
    load();
  }, [search]);

  async function openDetail(itemId) {
    try {
      const payload = await api(`/api/items/${itemId}`);
      setDetail(payload.item);
      setDrawerOpen(true);
    } catch (error) {
      notify(error.message, "error");
    }
  }

  return html`
    <${Stack} spacing=${UI.spacingPage} className="page-enter">
      <${Card} className="glass-card" elevation=${0}>
        <${CardContent} className="page-surface" sx=${{ p: UI.cardPadding }}>
          <${SectionHeader}
            eyebrow="Item Center"
            title="商品中心"
            description="统一查看商品、事件类型、最近发现时间和关联订阅数。"
          />
          <${TextField}
            label="搜索商品标题或商品 ID"
            value=${search}
            onChange=${(event) => setSearch(event.target.value)}
            fullWidth=${true}
            sx=${{ mt: UI.spacingSection }}
          />
        <//>
      <//>

      <${Card} className="glass-table" elevation=${0}>
        <${CardContent} className="page-surface" sx=${{ p: UI.cardPadding }}>
          <${TableContainer} className="table-relaxed">
            <${Table} size="small">
              <${TableHead}>
                <${TableRow}>
                  <${TableCell}>商品<//>
                  <${TableCell}>当前价格<//>
                  <${TableCell}>最近发现<//>
                  <${TableCell}>关联订阅数<//>
                  <${TableCell}>最新事件<//>
                  <${TableCell} align="right">详情<//>
                <//>
              <//>
              <${TableBody}>
                ${items.map((item) => html`
                  <${TableRow} key=${item.item_id} hover=${true}>
                    <${TableCell}>
                      <${Stack} spacing=${0.5}>
                        <${Typography} variant="subtitle2">${item.title}<//>
                        <${Typography} variant="caption" color="text.secondary">${item.item_id}<//>
                      <//>
                    <//>
                    <${TableCell}>${formatMoney(item.price)}<//>
                    <${TableCell}>${formatTs(item.last_seen_at)}<//>
                    <${TableCell}>${item.subscription_count}<//>
                    <${TableCell}>${item.latest_event_type || "-"}<//>
                    <${TableCell} align="right">
                      <${Button} size="small" onClick=${() => openDetail(item.item_id)}>查看<//>
                    <//>
                  <//>
                `)}
              <//>
            <//>
          <//>
        <//>
      <//>

      <${Drawer}
        anchor="right"
        open=${drawerOpen}
        onClose=${() => setDrawerOpen(false)}
        PaperProps=${{ className: "glass-drawer" }}
      >
        <${Box} sx=${{ width: { xs: "100vw", md: 600 }, p: 3 }} className="page-enter">
          ${detail
            ? html`
                <${Stack} spacing=${2}>
                  <${Box}>
                    <${Typography} variant="overline" color="primary.main">Item Detail<//>
                    <${Typography} variant="h5" sx=${{ mt: 0.5 }}>${detail.item.title}<//>
                  <//>
                  <${Stack} direction="row" spacing=${UI.spacingCompact} flexWrap="wrap">
                    <${Chip} label=${`价格 ${formatMoney(detail.item.price)}`} color="primary" />
                    <${Chip} label=${detail.item.latest_event_type || "无事件"} variant="outlined" />
                  <//>
                  <${Button} href=${detail.item.url} target="_blank" variant="contained">
                    打开商品页
                  <//>
                  <${JsonPanel} title="商品摘要" value=${detail.item} />
                  <${JsonPanel} title="关联订阅" value=${detail.subscriptions || []} />
                  <${JsonPanel} title="价格历史" value=${detail.price_history || []} />
                  <${JsonPanel} title="通知记录" value=${detail.notifications || []} />
                  <${JsonPanel} title="抓取记录" value=${detail.fetch_runs || []} />
                <//>
              `
            : html`
                <${Box} sx=${{ display: "grid", placeItems: "center", minHeight: 240 }}>
                  <${CircularProgress} />
                <//>
              `}
        <//>
      <//>
    <//>
  `;
}

function RuntimePage({ notify }) {
  const [overview, setOverview] = useState(null);
  const [health, setHealth] = useState(null);
  const [runs, setRuns] = useState([]);
  const [loading, setLoading] = useState(true);

  async function load(refresh = false) {
    try {
      const [overviewPayload, healthPayload, runsPayload] = await Promise.all([
        api("/api/overview"),
        api(`/api/provider/health${refresh ? "?refresh=true" : ""}`),
        api("/api/fetch-runs?limit=20"),
      ]);
      setOverview(overviewPayload);
      setHealth(healthPayload.health);
      setRuns(runsPayload.items || []);
    } catch (error) {
      notify(error.message, "error");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    const timer = window.setInterval(() => load(false), 8000);
    return () => window.clearInterval(timer);
  }, []);

  return html`
    <${Stack} spacing=${UI.spacingPage} className="page-enter">
      ${loading ? html`<${LinearProgress} />` : null}
      <${Box} className="hero-grid">
        <${MetricCard}
          title="调度器"
          value=${overview?.scheduler_running ? "运行中" : "未运行"}
          caption=${`队列 ${overview?.queue_size || 0} / 执行中 ${overview?.inflight || 0}`}
        />
        <${MetricCard}
          title="Provider"
          value=${overview?.provider_mode || "-"}
          caption=${overview?.provider_error || "当前状态正常"}
          tone="secondary"
        />
        <${MetricCard}
          title="最近健康检查"
          value=${formatTs(health?.checked_at)}
          caption=${`auth: ${health?.auth || "-"}`}
          tone="success"
        />
      <//>

      <${Card} className="glass-card" elevation=${0}>
        <${CardContent} className="page-surface" sx=${{ p: UI.cardPadding }}>
          <${SectionHeader}
            eyebrow="Runtime"
            title="运行与远程 Worker"
            description="展示调度器状态、远程 /health 回包、认证状态和最近抓取结果。"
            action=${html`<${Button} variant="contained" onClick=${() => load(true)}>手动刷新健康检查<//>`}
          />
        <//>
      <//>

      <${Box} className="surface-grid cols-2">
        <${JsonPanel} title="健康详情" value=${health || {}} />
        <${JsonPanel} title="最近抓取记录" value=${runs} />
      <//>
    <//>
  `;
}

function ConfigPage({ notify }) {
  const [config, setConfig] = useState(null);
  const [values, setValues] = useState({});
  const [fieldErrors, setFieldErrors] = useState({});
  const [saveDiff, setSaveDiff] = useState(null);
  const [reloadResult, setReloadResult] = useState(null);

  async function load() {
    try {
      const payload = await api("/api/config");
      setConfig(payload.config);
      setValues(payload.config.values || {});
      setFieldErrors({});
    } catch (error) {
      notify(error.message, "error");
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function save() {
    try {
      const payload = await api("/api/config", { method: "PUT", body: { values } });
      setSaveDiff(payload.diff || {});
      setFieldErrors({});
      notify("配置已保存到覆盖层", "success");
    } catch (error) {
      setFieldErrors(error.payload?.field_errors || {});
      notify(error.message, "error");
    }
  }

  async function reload() {
    try {
      const payload = await api("/api/config/reload", { method: "POST" });
      setReloadResult(payload);
      notify("运行时配置已重载", "success");
      load();
    } catch (error) {
      notify(error.message, "error");
    }
  }

  function renderField(field) {
    const meta = config.schema[field] || {};
    if (meta.type === "bool") {
      return html`
        <${FormControlLabel}
          key=${field}
          control=${html`
            <${Switch}
              checked=${Boolean(values[field])}
              onChange=${(event) => setValues((current) => ({ ...current, [field]: event.target.checked }))}
            />
          `}
          label=${meta.description || field}
        />
      `;
    }

    const multiline = meta.type === "list" || field.includes("prompt") || field === "remote_headers";
    const renderedValue = meta.type === "list"
      ? (Array.isArray(values[field]) ? values[field].join("\n") : "")
      : (values[field] ?? "");

    return html`
      <${TextField}
        key=${field}
        label=${meta.description || field}
        type=${meta.type === "int" || meta.type === "float" ? "number" : "text"}
        value=${renderedValue}
        onChange=${(event) => setValues((current) => ({
          ...current,
          [field]: meta.type === "list"
            ? event.target.value.split("\n").map((item) => item.trim()).filter(Boolean)
            : event.target.value,
        }))}
        helperText=${fieldErrors[field] || meta.hint || ""}
        error=${Boolean(fieldErrors[field])}
        fullWidth=${true}
        multiline=${multiline}
        minRows=${multiline ? 3 : 1}
      />
    `;
  }

  if (!config) {
    return html`
      <${Box} sx=${{ display: "grid", placeItems: "center", py: 12 }}>
        <${CircularProgress} />
      <//>
    `;
  }

  return html`
    <${Stack} spacing=${UI.spacingPage} className="page-enter">
      <${Card} className="glass-card" elevation=${0}>
        <${CardContent} className="page-surface" sx=${{ p: UI.cardPadding }}>
          <${SectionHeader}
            eyebrow="Editable Runtime Config"
            title="配置中心"
            description=${`覆盖层文件: ${config.overlay_path}`}
            action=${html`
              <${Stack} direction="row" spacing=${UI.spacingCompact}>
                <${Button} variant="outlined" onClick=${load}>刷新<//>
                <${Button} variant="contained" onClick=${save}>保存<//>
                <${Button} color="secondary" variant="contained" onClick=${reload}>应用重载<//>
              <//>
            `}
          />
        <//>
      <//>

      ${config.groups.map((group) => html`
        <${Card} key=${group.id} className="glass-card" elevation=${0}>
          <${CardContent} className="page-surface" sx=${{ p: UI.cardPadding }}>
            <${Typography} variant="h6">${group.title}<//>
            <${Stack} spacing=${2} sx=${{ mt: 2 }}>
              ${group.fields.map((field) => renderField(field))}
            <//>
          <//>
        <//>
      `)}

      ${saveDiff ? html`<${JsonPanel} title="最近一次保存 diff" value=${saveDiff} />` : null}

      ${reloadResult
        ? html`
            <${Alert}
              severity=${reloadResult.provider_error ? "warning" : "success"}
              variant="filled"
            >
              ${reloadResult.admin_server_restart_required
                ? "管理后台地址相关配置已变更，需要重启插件后生效。"
                : "运行时配置已生效。"}
            <//>
          `
        : null}
    <//>
  `;
}

function App() {
  const [route, setRouteState] = useState(getRoute());
  const [authenticated, setAuthenticated] = useState(false);
  const [booting, setBooting] = useState(true);
  const [loginLoading, setLoginLoading] = useState(false);
  const [loginError, setLoginError] = useState("");
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [snack, setSnack] = useState({ open: false, message: "", severity: "success" });
  const isMobile = useMediaQuery(theme.breakpoints.down("md"));

  function notify(message, severity = "success") {
    setSnack({ open: true, message, severity });
  }

  async function boot() {
    try {
      await api("/api/overview");
      setAuthenticated(true);
    } catch (error) {
      if (error.code !== "UNAUTHORIZED") {
        notify(error.message, "error");
      }
      setAuthenticated(false);
    } finally {
      setBooting(false);
    }
  }

  useEffect(() => {
    boot();
    const onHashChange = () => setRouteState(getRoute());
    window.addEventListener("hashchange", onHashChange);
    return () => window.removeEventListener("hashchange", onHashChange);
  }, []);

  async function login(apiKey) {
    setLoginLoading(true);
    setLoginError("");
    try {
      await api("/api/admin/login", { method: "POST", body: { api_key: apiKey } });
      setAuthenticated(true);
      notify("登录成功", "success");
      boot();
    } catch (error) {
      setLoginError(error.message);
    } finally {
      setLoginLoading(false);
    }
  }

  async function logout() {
    try {
      await api("/api/admin/logout", { method: "POST" });
    } catch (_) {
      // ignore
    }
    setAuthenticated(false);
  }

  if (booting) {
    return html`
      <${ThemeProvider} theme=${theme}>
        <${CssBaseline} />
        <${Box} sx=${{ minHeight: "100vh", display: "grid", placeItems: "center" }} className="shell-bg">
          <${CircularProgress} />
        <//>
      <//>
    `;
  }

  if (!authenticated) {
    return html`
      <${ThemeProvider} theme=${theme}>
        <${CssBaseline} />
        <${LoginView} loading=${loginLoading} error=${loginError} onLogin=${login} />
      <//>
    `;
  }

  const currentNav = NAV_ITEMS.find((item) => item.key === route) || NAV_ITEMS[0];

  const drawer = html`
    <${Box} sx=${{ width: 288 }} className="glass-sidebar sidebar-surface">
      <${Stack} spacing=${UI.spacingPage}>
        <${Stack} direction="row" spacing=${1.5} alignItems="center">
          <${Box} className="sidebar-logo">鱼<//>
          <${Box}>
            <${Typography} variant="subtitle2" color="primary.main">Goofish Catcher<//>
            <${Typography} variant="h6">管理后台<//>
          <//>
        <//>

        <${List} disablePadding=${true}>
          ${NAV_ITEMS.map((item) => html`
            <${ListItemButton}
              key=${item.key}
              selected=${route === item.key}
              onClick=${() => {
                setRoute(item.key);
                setRouteState(item.key);
                setDrawerOpen(false);
              }}
              className="sidebar-nav-item"
              sx=${{
                mb: 0.75,
                px: 1.75,
                py: 1.1,
                bgcolor: route === item.key ? alpha("#ffffff", 0.62) : "transparent",
                boxShadow: route === item.key ? "0 18px 28px rgba(37, 99, 235, 0.12)" : "none",
              }}
            >
              <${ListItemText}
                primary=${item.label}
                secondary=${item.eyebrow}
                primaryTypographyProps=${{ fontWeight: 700 }}
                secondaryTypographyProps=${{ fontSize: 12 }}
              />
            <//>
          `)}
        <//>

        <hr className="soft-divider" />

        <${Card} className="glass-card sidebar-section-card" elevation=${0}>
          <${CardContent} sx=${{ p: UI.spacingSection }}>
            <${Typography} variant="subtitle2">后台特性<//>
            <${Stack} spacing=${1.1} sx=${{ mt: 1.25 }}>
              <${Chip} label="API Key 登录" color="primary" />
              <${Chip} label="5-10 秒轮询刷新" variant="outlined" />
              <${Chip} label="本地地址默认 127.0.0.1" variant="outlined" />
            <//>
          <//>
        <//>
      <//>
    <//>
  `;

  return html`
    <${ThemeProvider} theme=${theme}>
      <${CssBaseline} />
      <${Box} className="shell-bg shell-layout">
        ${isMobile
          ? html`
              <${Drawer}
                open=${drawerOpen}
                onClose=${() => setDrawerOpen(false)}
                PaperProps=${{ className: "glass-drawer" }}
              >
                ${drawer}
              <//>
            `
          : html`
              <${Box} className="shell-sidebar-wrap">
                ${drawer}
              <//>
            `}

        <${Box} className="shell-main" sx=${{ minWidth: 0 }}>
          <${Box} className="shell-main-inner">
          <${AppBar}
            position="sticky"
            elevation=${0}
            className="glass-topbar shell-topbar"
            sx=${{ top: 0 }}
          >
            <${Toolbar} className="topbar-inner" sx=${{ minHeight: 88, px: { xs: 2.5, md: 3.5 } }}>
              ${isMobile
                ? html`<${IconButton} onClick=${() => setDrawerOpen(true)} sx=${{ mr: 1.25 }}>菜单<//>`
                : null}
              <${Box} sx=${{ flex: 1 }}>
                <${Typography} variant="overline" color="primary.main">${currentNav.eyebrow}<//>
                <${Typography} variant="h6">${currentNav.label}<//>
              <//>
              <${Stack} direction="row" spacing=${UI.spacingCompact} alignItems="center">
                <${Chip} label="Material 3 + Glass" variant="outlined" />
                <${Button} onClick=${logout}>退出登录<//>
              <//>
            <//>
          <//>

          <${Container} maxWidth=${false} className="shell-content" disableGutters=${true}>
            ${route === "dashboard" ? html`<${DashboardPage} notify=${notify} />` : null}
            ${route === "subscriptions" ? html`<${SubscriptionsPage} notify=${notify} />` : null}
            ${route === "items" ? html`<${ItemsPage} notify=${notify} />` : null}
            ${route === "runtime" ? html`<${RuntimePage} notify=${notify} />` : null}
            ${route === "config" ? html`<${ConfigPage} notify=${notify} />` : null}
          <//>
        <//>
        <//>
      <//>

      <${Snackbar}
        open=${snack.open}
        autoHideDuration=${3200}
        onClose=${() => setSnack((current) => ({ ...current, open: false }))}
      >
        <${Alert}
          severity=${snack.severity}
          variant="filled"
          onClose=${() => setSnack((current) => ({ ...current, open: false }))}
        >
          ${snack.message}
        <//>
      <//>
    <//>
  `;
}

createRoot(document.getElementById("root")).render(html`<${App} />`);
