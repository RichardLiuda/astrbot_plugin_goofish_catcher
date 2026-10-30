import {
	Alert,
	Button,
	Chip,
	LinearProgress,
	Stack,
	Table,
	TableBody,
	TableCell,
	TableContainer,
	TableHead,
	TableRow,
	Typography,
	html,
	startTransition,
	useEffect,
	useState
} from '../deps.js'
import { UI } from '../constants.js'
import { api, fetchRunChipProps, formatTs } from '../utils.js'
import {
	EmptyState,
	InfoList,
	PageHeader,
	StatCard,
	SurfaceCard
} from '../components.js'

export function RuntimePage({ notify }) {
	const [overview, setOverview] = useState(null)
	const [health, setHealth] = useState(null)
	const [runs, setRuns] = useState([])
	const [loading, setLoading] = useState(true)

	async function load(refresh = false) {
		try {
			const [overviewPayload, healthPayload, runsPayload] =
				await Promise.all([
					api('/api/overview'),
					api(
						`/api/provider/health${refresh ? '?refresh=true' : ''}`
					),
					api('/api/fetch-runs?limit=20')
				])
			startTransition(() => {
				setOverview(overviewPayload)
				setHealth(healthPayload.health)
				setRuns(runsPayload.items || [])
			})
		} catch (error) {
			notify(error.message, 'error')
		} finally {
			setLoading(false)
		}
	}

	useEffect(() => {
		load()
		const timer = window.setInterval(() => load(false), 8000)
		return () => window.clearInterval(timer)
	}, [])

	const healthItems = [
		{
			label: 'Provider 模式',
			value: health?.provider || overview?.provider_mode || '-'
		},
		{ label: 'Provider 状态', value: health?.ok ? '可用' : '异常' },
		{ label: '认证状态', value: health?.auth || '-' },
		{
			label: '登录态文件',
			value:
				health?.storage_state === null ||
				health?.storage_state === undefined
					? '-'
					: health.storage_state
						? '已就绪'
						: '未找到'
		},
		{ label: '最近健康检查', value: formatTs(health?.checked_at) },
		{
			label: '队列 / 执行中',
			value: `${overview?.queue_size || 0} / ${overview?.inflight || 0}`
		}
	]

	return html`
		<${Stack} spacing=${UI.pageGap} className="page-enter page-stack">
			<${PageHeader}
				title="运行状态"
				description="关注 Provider 健康、认证状态与最近抓取执行结果。"
				action=${html`
					<${Button} variant="contained" onClick=${() => load(true)}>
						刷新健康检查
					<//>
				`}
			/>

			${loading ? html`<${LinearProgress} />` : null}

			<div className="stats-grid">
				<${StatCard}
					label="调度器"
					value=${overview?.scheduler_running ? '运行中' : '未运行'}
					hint=${`队列 ${overview?.queue_size || 0}，执行中 ${overview?.inflight || 0}`}
					tone="primary"
				/>
				<${StatCard}
					label="Provider"
					value=${overview?.provider_mode || '-'}
					hint=${overview?.provider_error || '当前状态正常'}
					tone="secondary"
				/>
				<${StatCard}
					label="认证状态"
					value=${health?.auth || '-'}
					hint=${health?.storage_state
						? '登录态文件已就绪'
						: '登录态文件待确认'}
					tone="success"
				/>
				<${StatCard}
					label="最近健康检查"
					value=${formatTs(health?.checked_at)}
					hint="默认每 8 秒自动刷新"
					tone="warning"
				/>
			</div>

			<div className="content-grid runtime-grid">
				<${SurfaceCard}
					className="runtime-summary-card"
					title="状态摘要"
					description="快速确认当前是否可以正常抓取。"
				>
					${health?.provider_error || overview?.provider_error
						? html`<${Alert}
								severity="error"
								variant="outlined"
								sx=${{ mb: 2 }}
							>
								${health?.provider_error ||
								overview?.provider_error}
							<//>`
						: null}
					<${InfoList} items=${healthItems} />
				<//>

				<${SurfaceCard}
					className="runtime-runs-card"
					title="最近抓取记录"
					description="展示最近 20 次抓取执行状态。"
				>
					${runs.length
						? html`
								<${TableContainer}
									className="table-wrap compact-table runtime-runs-table"
								>
									<${Table} size="small">
										<${TableHead}>
											<${TableRow}>
												<${TableCell}>关键词<//>
												<${TableCell}>状态<//>
												<${TableCell}>开始 / 结束<//>
												<${TableCell}>商品数<//>
												<${TableCell}>错误<//>
											<//>
										<//>
										<${TableBody}>
											${runs.map((item) => {
												const chip = fetchRunChipProps(
													item.status
												)
												return html`
													<${TableRow} key=${item.id}>
														<${TableCell}
															className="table-primary-cell runtime-runs-keyword-cell"
														>
															<div className="table-primary-copy">
																<${Typography}
																	variant="body2"
																	className="table-primary-title"
																>
																	${item.keyword}
																<//>
																<${Typography}
																	variant="caption"
																	color="text.secondary"
																	className="table-primary-meta"
																>
																	${item.umo}
																<//>
															</div>
														<//>
														<${TableCell}>
															<${Chip}
																size="small"
																label=${chip.label}
																color=${chip.color}
																variant=${chip.variant}
															/>
														<//>
														<${TableCell}>
															<div className="runtime-runs-time">
															<${Typography}
																variant="body2"
																>${formatTs(
																	item.started_at
																)}<//
															>
															<${Typography}
																variant="caption"
																color="text.secondary"
															>
																${formatTs(
																	item.finished_at
																)}
															<//>
															</div>
														<//>
														<${TableCell}
															>${item.items_count}<//
														>
														<${TableCell}
															>${item.err_msg ||
															item.err_type ||
															'-'}<//
														>
													<//>
												`
											})}
										<//>
									<//>
								<//>
							`
						: html`<${EmptyState}
								title="暂无抓取记录"
								description="开始执行订阅后，这里会出现抓取结果。"
							/>`}
				<//>
			</div>
		<//>
	`
}
