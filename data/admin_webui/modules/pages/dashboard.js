import {
	Alert,
	Box,
	Button,
	CircularProgress,
	Stack,
	html,
	startTransition,
	useEffect,
	useState
} from '../deps.js'
import { UI } from '../constants.js'
import { api, formatTs } from '../utils.js'
import {
	AlertFeed,
	AppTextField,
	InfoList,
	PageHeader,
	QueryPreviewPanel,
	StatCard,
	SurfaceCard,
	TrendFeed
} from '../components.js'

export function DashboardPage({ notify }) {
	const [overview, setOverview] = useState(null)
	const [query, setQuery] = useState({ keyword: '', pages: 1 })
	const [preview, setPreview] = useState(null)
	const [loading, setLoading] = useState(true)

	async function load() {
		try {
			const payload = await api('/api/overview')
			startTransition(() => setOverview(payload))
		} catch (error) {
			notify(error.message, 'error')
		} finally {
			setLoading(false)
		}
	}

	useEffect(() => {
		load()
		const timer = window.setInterval(load, 8000)
		return () => window.clearInterval(timer)
	}, [])

	async function runQuery() {
		try {
			const payload = await api('/api/query', {
				method: 'POST',
				body: {
					keyword: query.keyword,
					pages: Number(query.pages || 1)
				}
			})
			startTransition(() => setPreview(payload.preview))
			notify('临时查询已完成', 'success')
		} catch (error) {
			notify(error.message, 'error')
		}
	}

	if (loading && !overview) {
		return html`
			<${Box} sx=${{ display: 'grid', placeItems: 'center', py: 12 }}>
				<${CircularProgress} />
			<//>
		`
	}

	const health = overview?.provider_health || {}
	const healthItems = [
		{ label: '抓取模式', value: overview?.provider_mode || '-' },
		{
			label: 'Provider 状态',
			value: overview?.provider_available ? '可用' : '异常'
		},
		{
			label: '调度器',
			value: overview?.scheduler_running ? '运行中' : '未运行'
		},
		{
			label: '最近检查',
			value: formatTs(overview?.provider_health_checked_at)
		},
		{
			label: '认证状态',
			value:
				health.auth ||
				(overview?.provider_mode === 'playwright_local'
					? '本地模式'
					: '-')
		},
		{
			label: '登录态文件',
			value:
				health.storage_state === undefined ||
				health.storage_state === null
					? '-'
					: health.storage_state
						? '已就绪'
						: '未找到'
		}
	]

	return html`
		<${Stack} spacing=${UI.pageGap} className="page-enter page-stack">
			<${PageHeader}
				title="控制台总览"
				description="保留运行决策最需要看的状态、告警和快速查询。"
			/>

			<div className="stats-grid">
				<${StatCard}
					label="订阅数量"
					value=${`${overview?.enabled_subscriptions || 0} / ${overview?.total_subscriptions || 0}`}
					hint=${`启用 ${overview?.enabled_subscriptions || 0}，暂停 ${overview?.paused_subscriptions || 0}`}
					tone="primary"
				/>
				<${StatCard}
					label="24 小时成功率"
					value=${`${Number(overview?.success_rate_24h || 0).toFixed(1)}%`}
					hint=${`成功 ${overview?.success_runs_24h || 0} 次，失败 ${overview?.failed_runs_24h || 0} 次`}
					tone="success"
				/>
				<${StatCard}
					label="队列 / 执行中"
					value=${`${overview?.queue_size || 0} / ${overview?.inflight || 0}`}
					hint=${`Worker 数量 ${overview?.workers || 0}`}
					tone="secondary"
				/>
				<${StatCard}
					label="最近告警"
					value=${overview?.recent_alerts?.length || 0}
					hint="展示最近业务与运行异常"
					tone="warning"
				/>
			</div>

			<div className="content-grid two-column">
				<${Stack} spacing=${UI.pageGap}>
					<${SurfaceCard}
						title="临时查询"
						description="不创建订阅，直接执行一次推荐分析。"
					>
						<div className="filter-grid">
							<${AppTextField}
								label="关键词"
								value=${query.keyword}
								onChange=${(event) =>
									setQuery((current) => ({
										...current,
										keyword: event.target.value
									}))}
								hint="输入你想临时分析的关键词"
							/>
							<${AppTextField}
								label="页数"
								type="number"
								value=${query.pages}
								onChange=${(event) =>
									setQuery((current) => ({
										...current,
										pages: event.target.value
									}))}
								wrapperSx=${{ width: { xs: '100%', md: 120 } }}
							/>
							<${Button}
								variant="contained"
								onClick=${runQuery}
								disabled=${!query.keyword.trim()}
							>
								开始分析
							<//>
						</div>

						${preview
							? html`<${Box} sx=${{ mt: 3 }}
									><${QueryPreviewPanel}
										title="查询结果"
										preview=${preview}
								/><//>`
							: null}
					<//>
				<//>
				<${Stack} spacing=${UI.pageGap}>
					<${SurfaceCard}
						title="运行状态"
						description="当前 Provider 与调度器的核心状态。"
					>
						${overview?.provider_error
							? html`<${Alert}
									severity="error"
									variant="outlined"
									sx=${{ mb: 2 }}
								>
									${overview.provider_error}
								<//>`
							: null}
						<${InfoList} items=${healthItems} />
					<//>
					<${SurfaceCard}
						title="最近告警"
						description="帮助快速确认当前是否需要手动介入。"
					>
						<${AlertFeed} items=${overview?.recent_alerts || []} />
					<//>
					<${SurfaceCard}
						title="近 7 天趋势"
						description="按天查看上新与降价通知数量。"
					>
						<${TrendFeed} items=${overview?.trends || []} />
					<//>
				<//>
			</div>
		<//>
	`
}
