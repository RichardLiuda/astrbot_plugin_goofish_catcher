import {
	Box,
	Button,
	Chip,
	CircularProgress,
	Drawer,
	Stack,
	Table,
	TableBody,
	TableCell,
	TableContainer,
	TableHead,
	TableRow,
	Typography,
	html
} from '../deps.js'
import { UI } from '../constants.js'
import {
	fetchRunChipProps,
	formatMoney,
	formatTs,
	statusChipProps
} from '../utils.js'
import { EmptyState, InfoList, SurfaceCard } from '../components.js'

export function ItemDetailContent({
	detail,
	onFocusSubscription,
	onRunSubscriptionAction,
	onDelete,
	onDeepSearch,
	deepSearchLoading
}) {
	const detailItem = detail?.item
	const deepAnalysis = detail?.deep_analysis || null
	const mainImage = deepAnalysis?.image_urls?.[0] || ''

	return html`
		${detail
			? html`
					<${Stack} spacing=${UI.pageGap}>
						<${Box}>
							<${Typography} variant="h5"
								>${detailItem?.title || '-'}<//
							>
							<${Typography}
								variant="body2"
								color="text.secondary"
								sx=${{ mt: 0.75 }}
							>
								${detailItem?.item_id || '-'}
							<//>
						<//>

						<div className="chip-row">
							<${Chip}
								label=${formatMoney(detailItem?.price)}
								color="primary"
							/>
							<${Chip}
								label=${detailItem?.latest_event_type || '无事件'}
								variant="outlined"
							/>
							<${Button}
								variant="outlined"
								href=${detailItem?.url}
								target="_blank"
							>
								打开商品页
							<//>
							${onDelete && detailItem?.item_id
								? html`
										<${Button}
											variant="outlined"
											color="error"
											onClick=${() => onDelete(detailItem.item_id)}
										>
											删除此记录
										<//>
									`
								: null}
						</div>

						<${SurfaceCard} title="基本信息">
							<${InfoList}
								items=${[
									{
										label: '商品 ID',
										value: detailItem?.item_id || '-'
									},
									{
										label: '发布时间',
										value: formatTs(detailItem?.publish_time)
									},
									{
										label: '首次发现',
										value: formatTs(detailItem?.first_seen_at)
									},
									{
										label: '最近发现',
										value: formatTs(detailItem?.last_seen_at)
									},
									{
										label: '关联订阅数',
										value: String(
											detailItem?.subscription_count || 0
										)
									}
								]}
							/>
						<//>

						<${SurfaceCard}
							title="深度分析"
							description="候选推荐前抓取的商品详情、卖家信用和风险结论。"
						>
							${deepAnalysis
								? html`
										<${Stack} spacing=${2}>
											${mainImage
												? html`<img
														src=${mainImage}
														alt=${detailItem?.title || '商品主图'}
														className="detail-main-image"
													/>`
												: null}
											<div className="chip-row">
												<${Chip}
													label=${`信用 ${deepAnalysis.credit_status || 'unknown'}`}
													color=${deepAnalysis.credit_status === 'good'
														? 'success'
														: deepAnalysis.credit_status === 'bad'
															? 'error'
															: 'default'}
													variant="outlined"
												/>
												<${Chip}
													label=${deepAnalysis.status || 'passed'}
													color=${deepAnalysis.status === 'rejected'
														? 'error'
														: 'success'}
													variant="outlined"
												/>
											</div>
											<${InfoList}
												items=${[
													{
														label: '卖家信用',
														value:
															deepAnalysis.credit_reason ||
															deepAnalysis.credit_status ||
															'-'
													},
													{
														label: '推荐/过滤理由',
														value: deepAnalysis.summary || '-'
													},
													{
														label: '风险说明',
														value: deepAnalysis.risk || '-'
													},
													{
														label: '想要人数',
														value:
															deepAnalysis.want_count == null
																? '-'
																: String(deepAnalysis.want_count)
													},
													{
														label: '浏览量',
														value:
															deepAnalysis.browse_count == null
																? '-'
																: String(deepAnalysis.browse_count)
													},
													{
														label: '分析时间',
														value: formatTs(deepAnalysis.analyzed_at)
													},
													{
														label: '图片链接',
														value: deepAnalysis.image_urls?.join('，') || '-'
													}
												]}
											/>
										<//>
									`
								: html`
										<${Stack} spacing=${1.5} alignItems="flex-start">
											<${EmptyState}
												title="暂无深度分析"
												description="商品进入推荐候选后会缓存详情分析结果，也可以手动触发。"
											/>
											${onDeepSearch && detailItem?.item_id
												? html`
														<${Button}
															variant="contained"
															size="small"
															disabled=${deepSearchLoading}
															onClick=${() => onDeepSearch(detailItem.item_id)}
														>
															${deepSearchLoading
																? html`<${CircularProgress} size=${16} sx=${{ mr: 1 }} />`
																: null}
															触发深度搜索
														<//>
													`
												: null}
										<//>
									`}
						<//>

						<${SurfaceCard}
							title="关联订阅"
							description="在商品上下文里直接筛选、检查或暂停关联订阅。"
						>
							${detail.subscriptions?.length
								? html`
										<${TableContainer}
											className="table-wrap compact-table managed-table"
										>
											<${Table} size="small">
												<${TableHead}>
													<${TableRow}>
														<${TableCell}
															className="table-primary-cell"
														>
															关键词
														<//>
														<${TableCell}>状态<//>
														<${TableCell}>最后价格<//>
														<${TableCell}>最后关联时间<//>
														<${TableCell}
															align="right"
															className="table-action-cell"
														>
															操作
														<//>
													<//>
												<//>
												<${TableBody}>
													${detail.subscriptions.map((item) => {
														const chip = statusChipProps(
															item.enabled,
															item.paused_reason
														)
														return html`
															<${TableRow}
																key=${item.sub_id}
																hover=${true}
															>
																<${TableCell}
																	className="table-primary-cell"
																>
																	<div className="table-primary-copy">
																		<${Typography}
																			variant="subtitle2"
																			className="table-primary-title"
																		>
																			${item.keyword}
																		<//>
																		<${Typography}
																			variant="caption"
																			color="text.secondary"
																			className="table-primary-meta"
																		>
																			${`#${item.sub_id} · UMO ${item.umo}`}
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
																<${TableCell}
																	>${formatMoney(item.last_price)}<//
																>
																<${TableCell}
																	>${formatTs(item.last_seen_at)}<//
																>
																<${TableCell}
																	align="right"
																	className="table-action-cell"
																>
																	<div className="table-actions">
																		<${Button}
																			size="small"
																			onClick=${() =>
																				onFocusSubscription(
																					item.sub_id
																				)}
																		>
																			按此查看
																		<//>
																		<${Button}
																			size="small"
																			onClick=${() =>
																				onRunSubscriptionAction(
																					item.sub_id,
																					'check',
																					detailItem?.item_id ||
																						''
																				)}
																		>
																			检查
																		<//>
																		<${Button}
																			size="small"
																			onClick=${() =>
																				onRunSubscriptionAction(
																					item.sub_id,
																					item.enabled
																						? 'pause'
																						: 'resume',
																					detailItem?.item_id ||
																						''
																				)}
																		>
																			${item.enabled
																				? '暂停'
																				: '恢复'}
																		<//>
																	</div>
																<//>
															<//>
														`
													})}
												<//>
											<//>
										<//>
									`
								: html`<${EmptyState}
										title="没有关联订阅"
										description="这个商品还没有命中过任何订阅条目。"
									/>`}
						<//>

						<${SurfaceCard}
							title="价格历史"
							description="默认展示最近 20 条价格记录。"
						>
							${detail.price_history?.length
								? html`
										<${TableContainer}
											className="table-wrap compact-table"
										>
											<${Table} size="small">
												<${TableHead}>
													<${TableRow}>
														<${TableCell}>时间<//>
														<${TableCell}>价格<//>
														<${TableCell}>来源<//>
														<${TableCell}>关键词<//>
													<//>
												<//>
												<${TableBody}>
													${detail.price_history
														.slice(0, 20)
														.map(
															(item, index) => html`
																<${TableRow}
																	key=${`${item.observed_at}-${index}`}
																>
																	<${TableCell}
																		>${formatTs(
																			item.observed_at
																		)}<//
																	>
																	<${TableCell}
																		>${formatMoney(item.price)}<//
																	>
																	<${TableCell}
																		>${item.source || '-'}<//
																	>
																	<${TableCell}
																		>${item.keyword || '-'}<//
																	>
																<//>
															`
														)}
												<//>
											<//>
										<//>
									`
								: html`<${EmptyState}
										title="暂无价格历史"
										description="抓到同一商品的价格变化后会显示在这里。"
									/>`}
						<//>

						<${SurfaceCard}
							title="通知记录"
							description="默认展示最近 15 条通知。"
						>
							${detail.notifications?.length
								? html`
										<${TableContainer}
											className="table-wrap compact-table"
										>
											<${Table} size="small">
												<${TableHead}>
													<${TableRow}>
														<${TableCell}>时间<//>
														<${TableCell}>事件<//>
														<${TableCell}
															className="table-primary-cell"
														>
															关键词
														<//>
													<//>
												<//>
												<${TableBody}>
													${detail.notifications
														.slice(0, 15)
														.map(
															(item, index) => html`
																<${TableRow}
																	key=${`${item.sent_at}-${index}`}
																>
																	<${TableCell}
																		>${formatTs(
																			item.sent_at
																		)}<//
																	>
																	<${TableCell}
																		>${item.event_type || '-'}<//
																	>
																	<${TableCell}
																		className="table-primary-cell"
																	>
																		<div className="table-primary-copy">
																			<${Typography}
																				variant="body2"
																				className="table-primary-title"
																			>
																				${item.keyword || '-'}
																			<//>
																			<${Typography}
																				variant="caption"
																				color="text.secondary"
																				className="table-primary-meta"
																			>
																				${item.umo || '-'}
																			<//>
																		</div>
																	<//>
																<//>
															`
														)}
												<//>
											<//>
										<//>
									`
								: html`<${EmptyState}
										title="暂无通知记录"
										description="发送过通知后会显示在这里。"
									/>`}
						<//>

						<${SurfaceCard}
							title="抓取记录"
							description="默认展示最近 15 次抓取结果。"
						>
							${detail.fetch_runs?.length
								? html`
										<${TableContainer}
											className="table-wrap compact-table"
										>
											<${Table} size="small">
												<${TableHead}>
													<${TableRow}>
														<${TableCell}>开始时间<//>
														<${TableCell}>状态<//>
														<${TableCell}>商品数<//>
														<${TableCell}>错误<//>
													<//>
												<//>
												<${TableBody}>
													${detail.fetch_runs
														.slice(0, 15)
														.map((item) => {
															const chip =
																fetchRunChipProps(
																	item.status
																)
															return html`
																<${TableRow}
																	key=${item.id}
																>
																	<${TableCell}
																		>${formatTs(
																			item.started_at
																		)}<//
																	>
																	<${TableCell}>
																		<${Chip}
																			size="small"
																			label=${chip.label}
																			color=${chip.color}
																			variant=${chip.variant}
																		/>
																	<//>
																	<${TableCell}
																		>${item.items_count}<//
																	>
																	<${TableCell}
																		>${item.err_msg || '-'}<//
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
										description="开始抓取后这里会展示每次执行的结果。"
									/>`}
						<//>
					<//>
				`
			: html`
					<${Box}
						sx=${{
							display: 'grid',
							placeItems: 'center',
							minHeight: 240
						}}
					>
						<${CircularProgress} />
					<//>
				`}
	`
}

export function ItemDetailDrawer({
	open,
	detail,
	onClose,
	onFocusSubscription,
	onRunSubscriptionAction,
	onDelete,
	onDeepSearch,
	deepSearchLoading
}) {
	return html`
		<${Drawer}
			anchor="right"
			open=${open}
			onClose=${onClose}
			PaperProps=${{ sx: { width: { xs: '100%', md: 760 } } }}
		>
			<${Box} className="detail-drawer">
				<${ItemDetailContent}
					detail=${detail}
					onFocusSubscription=${onFocusSubscription}
					onRunSubscriptionAction=${onRunSubscriptionAction}
					onDelete=${onDelete}
					onDeepSearch=${onDeepSearch}
					deepSearchLoading=${deepSearchLoading}
				/>
			<//>
		<//>
	`
}
