import {
	Alert,
	Box,
	Button,
	CircularProgress,
	Stack,
	Switch,
	Typography,
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

export function DashboardPage({
	notify,
	temporaryQuery,
	onTemporaryQueryChange,
	onRunTemporaryQuery
}) {
	const [overview, setOverview] = useState(null)
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
			value: health.auth || '-'
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
								value=${temporaryQuery.keyword}
								onChange=${(event) =>
									onTemporaryQueryChange({
										keyword: event.target.value
									})}
								hint="输入你想临时分析的关键词"
							/>
							<${AppTextField}
								label="页数"
								type="number"
								value=${temporaryQuery.pages}
								onChange=${(event) =>
									onTemporaryQueryChange({
										pages: event.target.value
								})}
								wrapperSx=${{ width: { xs: '100%', md: 120 } }}
							/>
							<${AppTextField}
								label="最低价"
								type="number"
								value=${temporaryQuery.price_min ?? ''}
								onChange=${(event) =>
									onTemporaryQueryChange({
										price_min: event.target.value
									})}
								wrapperSx=${{ width: { xs: '100%', md: 120 } }}
							/>
							<${AppTextField}
								label="最高价"
								type="number"
								value=${temporaryQuery.price_max ?? ''}
								onChange=${(event) =>
									onTemporaryQueryChange({
										price_max: event.target.value
									})}
								wrapperSx=${{ width: { xs: '100%', md: 120 } }}
							/>
							<${AppTextField}
								label="新发布范围"
								value=${temporaryQuery.new_publish_option ?? ''}
								onChange=${(event) =>
									onTemporaryQueryChange({
										new_publish_option: event.target.value
									})}
								hint="如 24小时内 / 7天内"
							/>
							<${AppTextField}
								label="地区"
								value=${temporaryQuery.region ?? ''}
								onChange=${(event) =>
									onTemporaryQueryChange({
										region: event.target.value
									})}
								hint="如 江苏/南京/全南京"
							/>
							<${Box} className="field-block">
								<div className="field-label">个人闲置</div>
								<${Stack}
									direction="row"
									alignItems="center"
									spacing=${1}
									sx=${{ minHeight: 44 }}
								>
									<${Switch}
										checked=${Boolean(temporaryQuery.personal_only)}
										onChange=${(event) =>
											onTemporaryQueryChange({
												personal_only: event.target.checked
											})}
									/>
									<${Typography} variant="body2" color="text.secondary">
										仅个人闲置
									<//>
								<//>
							<//>
							<${Box} className="field-block">
								<div className="field-label">包邮</div>
								<${Stack}
									direction="row"
									alignItems="center"
									spacing=${1}
									sx=${{ minHeight: 44 }}
								>
									<${Switch}
										checked=${Boolean(temporaryQuery.free_shipping)}
										onChange=${(event) =>
											onTemporaryQueryChange({
												free_shipping: event.target.checked
											})}
									/>
									<${Typography} variant="body2" color="text.secondary">
										仅包邮
									<//>
								<//>
							<//>
							<${Button}
								variant="contained"
								onClick=${onRunTemporaryQuery}
								disabled=${temporaryQuery.loading || !temporaryQuery.keyword.trim()}
								startIcon=${temporaryQuery.loading
									? html`<${CircularProgress}
											size=${16}
											color="inherit"
										/>`
									: null}
							>
								${temporaryQuery.loading ? '分析中...' : '开始分析'}
							<//>
						</div>

						${temporaryQuery.preview
							? html`<${Box} sx=${{ mt: 3 }}
									><${QueryPreviewPanel}
										title="查询结果"
										preview=${temporaryQuery.preview}
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
