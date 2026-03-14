import {
	Button,
	Chip,
	LinearProgress,
	MenuItem,
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
	useDeferredValue,
	useEffect,
	useMediaQuery,
	useState
} from '../deps.js'
import { UI } from '../constants.js'
import {
	api,
	formatMoney,
	formatTs,
	parseFilterTerms,
	shouldHideItemByTerms,
	statusChipProps
} from '../utils.js'
import { AppTextField, EmptyState, PageHeader, SurfaceCard } from '../components.js'
import { ItemDetailContent, ItemDetailDrawer } from './items-detail-drawer.js'

export function ItemsPage({ notify }) {
	const [filters, setFilters] = useState({
		search: '',
		subId: '',
		view: 'flat',
		blockedTerms: '',
		minPrice: '',
		maxPrice: '',
		sortBy: 'last_seen_at',
		sortOrder: 'desc'
	})
	const [items, setItems] = useState([])
	const [total, setTotal] = useState(0)
	const [loading, setLoading] = useState(true)
	const [detail, setDetail] = useState(null)
	const [drawerOpen, setDrawerOpen] = useState(false)
	const [subscriptionOptions, setSubscriptionOptions] = useState([])
	const isNarrowScreen = useMediaQuery('(max-width: 720px)')

	const deferredSearch = useDeferredValue(filters.search)

	async function loadSubscriptionOptions() {
		try {
			const payload = await api('/api/subscriptions/options')
			startTransition(() => {
				setSubscriptionOptions(payload.items || [])
			})
		} catch (error) {
			notify(error.message, 'error')
		}
	}

	async function load() {
		try {
			const params = new URLSearchParams({
				search: deferredSearch,
				sort_by: filters.sortBy,
				sort_order: filters.sortOrder
			})
			if (filters.subId) {
				params.set('sub_id', filters.subId)
			}
			if (filters.minPrice !== '') {
				params.set('min_price', filters.minPrice)
			}
			if (filters.maxPrice !== '') {
				params.set('max_price', filters.maxPrice)
			}
			const endpoint =
				filters.view === 'by_subscription'
					? '/api/items/by-subscription'
					: '/api/items'
			const payload = await api(`${endpoint}?${params.toString()}`)
			startTransition(() => {
				setItems(payload.items || [])
				setTotal(payload.total || 0)
			})
		} catch (error) {
			notify(error.message, 'error')
		} finally {
			setLoading(false)
		}
	}

	useEffect(() => {
		loadSubscriptionOptions()
	}, [])

	useEffect(() => {
		if (
			filters.view === 'by_subscription' &&
			filters.sortBy === 'subscription_count'
		) {
			setFilters((current) => ({
				...current,
				sortBy: 'last_seen_at'
			}))
		}
	}, [filters.view, filters.sortBy])

	useEffect(() => {
		setLoading(true)
		load()
	}, [
		deferredSearch,
		filters.subId,
		filters.view,
		filters.minPrice,
		filters.maxPrice,
		filters.sortBy,
		filters.sortOrder
	])

	async function loadItemDetail(itemId, reset = false) {
		if (reset) {
			setDetail(null)
		}
		const payload = await api(`/api/items/${itemId}`)
		startTransition(() => setDetail(payload.item))
		return payload.item
	}

	async function openDetail(itemId) {
		setDrawerOpen(true)
		try {
			await loadItemDetail(itemId, true)
		} catch (error) {
			setDrawerOpen(false)
			notify(error.message, 'error')
		}
	}

	async function runSubscriptionAction(subId, action, itemId = '') {
		try {
			await api(`/api/subscriptions/${subId}/${action}`, {
				method: 'POST'
			})
			await loadSubscriptionOptions()
			await load()
			if (itemId) {
				await loadItemDetail(itemId)
			}
			notify(
				action === 'check' ? '订阅已执行检查' : '订阅状态已更新',
				'success'
			)
		} catch (error) {
			notify(error.message, 'error')
		}
	}

	function focusSubscription(subId) {
		setDrawerOpen(false)
		setFilters((current) => ({
			...current,
			subId: String(subId),
			view: 'by_subscription'
		}))
	}

	const blockedTerms = parseFilterTerms(filters.blockedTerms)
	const visibleItems = items.filter(
		(item) => !shouldHideItemByTerms(item, blockedTerms)
	)
	const groupedItems = []
	if (filters.view === 'by_subscription') {
		const groups = new Map()
		for (const entry of visibleItems) {
			if (!groups.has(entry.sub_id)) {
				const chip = statusChipProps(entry.enabled, entry.paused_reason)
				const group = {
					sub_id: entry.sub_id,
					keyword: entry.keyword,
					umo: entry.umo,
					enabled: entry.enabled,
					paused_reason: entry.paused_reason,
					statusLabel: chip.label,
					statusColor: chip.color,
					statusVariant: chip.variant,
					last_seen_at: entry.last_seen_at,
					items: []
				}
				groups.set(entry.sub_id, group)
				groupedItems.push(group)
			}
			const group = groups.get(entry.sub_id)
			group.items.push(entry)
			group.last_seen_at = Math.max(
				group.last_seen_at || 0,
				entry.last_seen_at || 0
			)
		}
	}

	const selectedSubscription =
		subscriptionOptions.find(
			(option) => String(option.id) === String(filters.subId || '')
		) || null
	const hiddenByBlockedTerms = items.length - visibleItems.length
	const visibleTotal = visibleItems.length
	const hasCustomFilters = Boolean(
		filters.search.trim() ||
			filters.subId ||
			filters.view !== 'flat' ||
			filters.blockedTerms.trim() ||
			filters.minPrice !== '' ||
			filters.maxPrice !== '' ||
			filters.sortBy !== 'last_seen_at' ||
			filters.sortOrder !== 'desc'
	)

	if (isNarrowScreen && drawerOpen) {
		return html`
			<${Stack} spacing=${UI.pageGap} className="page-enter page-stack">
				<${PageHeader}
					title="商品详情"
					description="窄屏下切换为单页详情视图，返回后继续保留当前筛选条件。"
					action=${html`
						<${Button}
							variant="outlined"
							onClick=${() => setDrawerOpen(false)}
						>
							返回列表
						<//>
					`}
				/>

				<${ItemDetailContent}
					detail=${detail}
					onFocusSubscription=${focusSubscription}
					onRunSubscriptionAction=${runSubscriptionAction}
				/>
			<//>
		`
	}

	return html`
		<${Stack} spacing=${UI.pageGap} className="page-enter page-stack">
			<${PageHeader}
				title="商品中心"
				description="集中查看商品、按订阅分类浏览，并在商品上下文里直接处理关联订阅。"
			/>

			<${SurfaceCard}
				title="筛选"
				description=${`当前显示 ${visibleTotal} / ${total} 条${
					filters.view === 'by_subscription'
						? '订阅商品记录'
						: '聚合商品记录'
				}${hiddenByBlockedTerms ? `，已按屏蔽词隐藏 ${hiddenByBlockedTerms} 条` : ''}`}
				action=${hasCustomFilters
					? html`
							<${Button}
								variant="outlined"
								size="small"
								onClick=${() =>
									setFilters({
										search: '',
										subId: '',
										view: 'flat',
										blockedTerms: '',
										minPrice: '',
										maxPrice: '',
										sortBy: 'last_seen_at',
										sortOrder: 'desc'
									})}
							>
								重置
							<//>
						`
					: null}
			>
				<div className="items-filter-layout">
					<div className="items-filter-section">
						<div className="items-filter-section-title">检索与屏蔽</div>
						<div className="filter-grid items-filter-grid">
							<${AppTextField}
								label="搜索商品标题或商品 ID"
								value=${filters.search}
								onChange=${(event) =>
									setFilters((current) => ({
										...current,
										search: event.target.value
									}))}
								hint="支持标题关键词、商品 ID，也支持在按订阅视图里匹配订阅关键词。"
								wrapperSx=${{ gridColumn: { xs: 'auto', xl: 'span 2' } }}
							/>
							<${AppTextField}
								label="屏蔽词"
								value=${filters.blockedTerms}
								onChange=${(event) =>
									setFilters((current) => ({
										...current,
										blockedTerms: event.target.value
									}))}
								hint=${hiddenByBlockedTerms
									? `已按屏蔽词隐藏 ${hiddenByBlockedTerms} 条商品，多个词可用空格、逗号或换行分隔。`
									: '命中标题、描述、卖家、订阅关键词时将隐藏，多个词可用空格、逗号或换行分隔。'}
								wrapperSx=${{ gridColumn: { xs: 'auto', xl: 'span 2' } }}
							/>
							<${AppTextField}
								select=${true}
								label="订阅条目"
								value=${filters.subId}
								onChange=${(event) =>
									setFilters((current) => ({
										...current,
										subId: event.target.value
									}))}
								wrapperSx=${{ gridColumn: { xs: 'auto', lg: 'span 2' } }}
								hint=${selectedSubscription
									? `当前订阅：#${selectedSubscription.id} ${selectedSubscription.keyword}`
									: '可选，按某条订阅聚焦商品。'}
							>
								<${MenuItem} value="">全部订阅<//>
								${subscriptionOptions.map((option) => {
									const suffix = option.enabled ? '' : '（已暂停）'
									return html`
										<${MenuItem}
											key=${option.id}
											value=${String(option.id)}
										>
											${`#${option.id} ${option.keyword}${suffix}`}
										<//>
									`
								})}
							<//>
						</div>
					</div>
					<div className="items-filter-section items-filter-section-secondary">
						<div className="items-filter-section-title">视图与排序</div>
						<div className="filter-grid items-filter-grid items-filter-grid-compact">
							<${AppTextField}
								select=${true}
								label="视图模式"
								value=${filters.view}
								onChange=${(event) =>
									setFilters((current) => ({
										...current,
										view: event.target.value
									}))}
								hint="聚合商品用于去重查看；按订阅分类用于围绕监控条目管理。"
							>
								<${MenuItem} value="flat">聚合商品<//>
								<${MenuItem} value="by_subscription"
									>按订阅分类<//>
							<//>
							<${AppTextField}
								label="最低价格"
								type="number"
								value=${filters.minPrice}
								onChange=${(event) =>
									setFilters((current) => ({
										...current,
										minPrice: event.target.value
									}))}
								hint="留空表示不限。"
							/>
							<${AppTextField}
								label="最高价格"
								type="number"
								value=${filters.maxPrice}
								onChange=${(event) =>
									setFilters((current) => ({
										...current,
										maxPrice: event.target.value
									}))}
								hint="留空表示不限。"
							/>
							<${AppTextField}
								select=${true}
								label="排序字段"
								value=${filters.sortBy}
								onChange=${(event) =>
									setFilters((current) => ({
										...current,
										sortBy: event.target.value
									}))}
							>
								<${MenuItem} value="last_seen_at">最近发现<//>
								<${MenuItem} value="price">价格<//>
								<${MenuItem} value="publish_time">发布时间<//>
								<${MenuItem} value="title">标题<//>
								${filters.view === 'flat'
									? html`<${MenuItem}
											value="subscription_count"
										>
											订阅数
										<//>`
									: null}
							<//>
							<${AppTextField}
								select=${true}
								label="排序方向"
								value=${filters.sortOrder}
								onChange=${(event) =>
									setFilters((current) => ({
										...current,
										sortOrder: event.target.value
									}))}
							>
								<${MenuItem} value="desc">降序<//>
								<${MenuItem} value="asc">升序<//>
							<//>
						</div>
					</div>
				</div>
			<//>

			${filters.view === 'by_subscription'
				? html`
						<${SurfaceCard}
							title="按订阅分类"
							description="把商品还原到具体订阅条目下，便于逐条管理和快速检查。"
						>
							${loading ? html`<${LinearProgress} sx=${{ mb: 2 }} />` : null}
							${groupedItems.length
								? html`
										<${Stack} spacing=${UI.sectionGap}>
											${groupedItems.map(
												(group) => html`
													<${SurfaceCard}
														key=${group.sub_id}
														title=${`#${group.sub_id} ${group.keyword}`}
														description=${`${group.items.length} 条商品 · 最近发现 ${formatTs(group.last_seen_at)}`}
														action=${html`
															<div className="header-actions">
																<${Chip}
																	size="small"
																	label=${group.statusLabel}
																	color=${group.statusColor}
																	variant=${group.statusVariant}
																/>
																<${Button}
																	size="small"
																	onClick=${() =>
																		runSubscriptionAction(
																			group.sub_id,
																			'check'
																		)}
																>
																	立即检查
																<//>
																<${Button}
																	size="small"
																	onClick=${() =>
																		runSubscriptionAction(
																			group.sub_id,
																			group.enabled
																				? 'pause'
																				: 'resume'
																		)}
																>
																	${group.enabled
																		? '暂停'
																		: '恢复'}
																<//>
																${String(filters.subId || '') !== String(group.sub_id)
																	? html`
																			<${Button}
																				size="small"
																				onClick=${() =>
																					focusSubscription(
																						group.sub_id
																					)}
																			>
																				仅看此订阅
																			<//>
																		`
																	: null}
															</div>
														`}
													>
														<${TableContainer}
															className="table-wrap compact-table managed-table"
														>
															<${Table} size="small">
																<${TableHead}>
																	<${TableRow}>
																		<${TableCell}
																			className="table-primary-cell"
																		>
																			商品
																		<//>
																		<${TableCell}>价格<//>
																		<${TableCell}>最近发现<//>
																		<${TableCell}>最新事件<//>
																		<${TableCell}
																			align="right"
																			className="table-action-cell"
																		>
																			操作
																		<//>
																	<//>
																<//>
																<${TableBody}>
																	${group.items.map(
																		(item) => html`
																			<${TableRow}
																				key=${`${group.sub_id}-${item.item_id}`}
																				hover=${true}
																			>
																				<${TableCell}
																					className="table-primary-cell"
																				>
																					<div className="table-primary-copy item-primary-copy">
																						<${Typography}
																							variant="subtitle2"
																							className="table-primary-title item-primary-title"
																						>
																							${item.title}
																						<//>
																						<${Typography}
																							variant="caption"
																							color="text.secondary"
																							className="table-primary-meta"
																						>
																							${item.item_id}
																						<//>
																					</div>
																				<//>
																				<${TableCell}
																					>${formatMoney(item.price)}<//
																				>
																				<${TableCell}
																					>${formatTs(item.last_seen_at)}<//
																				>
																				<${TableCell}
																					>${item.latest_event_type || '-'}<//
																				>
																				<${TableCell}
																					align="right"
																					className="table-action-cell"
																				>
																					<div className="table-actions">
																						<${Button}
																							size="small"
																							onClick=${() =>
																								openDetail(
																									item.item_id
																								)}
																						>
																							查看详情
																						<//>
																						<${Button}
																							size="small"
																							variant="outlined"
																							href=${item.url}
																							target="_blank"
																						>
																							打开商品
																						<//>
																					</div>
																				<//>
																			<//>
																		`
																	)}
																<//>
															<//>
														<//>
													<//>
												`
											)}
										<//>
									`
								: html`
										<${EmptyState}
											title="没有匹配的订阅商品记录"
											description="可以切换回聚合商品视图，或缩小搜索条件后再试。"
										/>
									`}
						<//>
					`
				: html`
						<${SurfaceCard}
							title="商品列表"
							description="按商品维度聚合去重，便于先快速看盘，再进入明细处理。"
						>
							${loading ? html`<${LinearProgress} sx=${{ mb: 2 }} />` : null}
							${visibleItems.length
								? html`
										<${TableContainer}
											className="table-wrap relaxed-table managed-table"
										>
											<${Table} size="small">
												<${TableHead}>
													<${TableRow}>
														<${TableCell} className="table-primary-cell"
															>商品<//>
														<${TableCell}>价格<//>
														<${TableCell}>最近发现<//>
														<${TableCell}>订阅数<//>
														<${TableCell}>最新事件<//>
														<${TableCell}
															align="right"
															className="table-action-cell"
														>
															详情
														<//>
													<//>
												<//>
												<${TableBody}>
													${visibleItems.map(
														(item) => html`
															<${TableRow}
																key=${item.item_id}
																hover=${true}
															>
																<${TableCell}
																	className="table-primary-cell"
																>
																	<div className="table-primary-copy item-primary-copy">
																		<${Typography}
																			variant="subtitle2"
																			className="table-primary-title item-primary-title"
																		>
																			${item.title}
																		<//>
																		<${Typography}
																			variant="caption"
																			color="text.secondary"
																			className="table-primary-meta"
																		>
																			${item.item_id}
																		<//>
																	</div>
																<//>
																<${TableCell}
																	>${formatMoney(item.price)}<//
																>
																<${TableCell}
																	>${formatTs(item.last_seen_at)}<//
																>
																<${TableCell}
																	>${item.subscription_count}<//
																>
																<${TableCell}
																	>${item.latest_event_type || '-'}<//
																>
																<${TableCell}
																	align="right"
																	className="table-action-cell"
																>
																	<${Button}
																		size="small"
																		onClick=${() =>
																			openDetail(
																				item.item_id
																			)}
																	>
																		查看详情
																	<//>
																<//>
															<//>
														`
													)}
												<//>
											<//>
										<//>
									`
								: html`
										<${EmptyState}
											title="没有匹配的商品"
											description="输入标题关键词、商品 ID，或切换到按订阅分类视图继续查看。"
										/>
									`}
						<//>
					`}

			${!isNarrowScreen
				? html`
						<${ItemDetailDrawer}
							open=${drawerOpen}
							detail=${detail}
							onClose=${() => setDrawerOpen(false)}
							onFocusSubscription=${focusSubscription}
							onRunSubscriptionAction=${runSubscriptionAction}
						/>
					`
				: null}
		<//>
	`
}
