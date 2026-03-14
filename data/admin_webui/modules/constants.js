export const NAV_ITEMS = [
	{ key: 'dashboard', label: '总览', description: '关键指标与快速查询' },
	{ key: 'subscriptions', label: '订阅', description: '统一管理监控规则' },
	{ key: 'items', label: '商品', description: '查看商品与关联记录' },
	{
		key: 'runtime',
		label: '运行状态',
		description: '检查 Provider 与抓取情况'
	},
	{ key: 'config', label: '配置', description: '编辑运行时配置' }
]

export const UI = {
	cardPadding: { xs: 2.5, md: 3 },
	pageGap: 3,
	sectionGap: 2.5
}

export const FIELD_CONTROL_SX = {
	'& .MuiInputBase-root': {
		alignItems: 'flex-start',
		borderRadius: '16px',
		border: '1px solid rgba(167, 145, 102, 0.16)',
		backgroundColor: 'rgba(250, 246, 239, 0.92)',
		transition:
			'background-color 180ms ease, border-color 180ms ease, box-shadow 180ms ease',
		paddingInline: '14px',
		boxShadow: 'none',
		'&:hover': {
			backgroundColor: 'rgba(252, 248, 242, 0.98)',
			borderColor: 'rgba(159, 133, 80, 0.24)'
		},
		'&.Mui-focused': {
			backgroundColor: 'rgba(255, 252, 247, 0.98)',
			borderColor: 'rgba(159, 133, 80, 0.34)',
			boxShadow: '0 0 0 3px rgba(159, 133, 80, 0.08)'
		},
		'&.Mui-error': {
			borderColor: 'rgba(220, 38, 38, 0.28)',
			boxShadow: '0 0 0 3px rgba(220, 38, 38, 0.06)'
		}
	},
	'& .MuiInputBase-input': {
		padding: '15px 0',
		fontSize: '0.95rem',
		lineHeight: 1.55,
		color: '#30261a'
	},
	'& .MuiInputBase-input::placeholder': {
		color: 'rgba(123, 109, 90, 0.72)',
		opacity: 1
	},
	'& .MuiInputBase-inputMultiline': {
		paddingBlock: '15px'
	},
	'& .MuiSelect-select': {
		minHeight: 'unset',
		padding: '15px 26px 15px 0 !important'
	},
	'& .MuiSvgIcon-root': {
		color: '#8b7650'
	}
}
