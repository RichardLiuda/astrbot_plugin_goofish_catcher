import { createTheme } from './deps.js'

export const theme = createTheme({
	palette: {
		mode: 'light',
		primary: { main: '#9f8550' },
		secondary: { main: '#7d6942' },
		success: { main: '#16a34a' },
		warning: { main: '#d97706' },
		error: { main: '#dc2626' },
		background: {
			default: '#f6f1e7',
			paper: '#fdfaf4'
		},
		text: {
			primary: '#30261a',
			secondary: '#7b6d5a'
		}
	},
	shape: {
		borderRadius: 18
	},
	typography: {
		fontFamily:
			"'Avenir Next', 'Segoe UI Variable', 'PingFang SC', 'Noto Sans SC', sans-serif",
		h4: { fontWeight: 720, letterSpacing: '-0.03em' },
		h5: { fontWeight: 700, letterSpacing: '-0.02em' },
		h6: { fontWeight: 700 },
		subtitle1: { fontWeight: 650 },
		subtitle2: { fontWeight: 650 },
		button: { textTransform: 'none', fontWeight: 650 }
	},
	components: {
		MuiCssBaseline: {
			styleOverrides: {
				body: {
					minHeight: '100vh'
				}
			}
		},
		MuiAppBar: {
			styleOverrides: {
				root: {
					borderRadius: 24,
					background: 'rgba(253, 250, 244, 0.9)',
					color: '#30261a',
					border: '1px solid rgba(167, 145, 102, 0.16)',
					boxShadow: '0 12px 30px rgba(112, 93, 60, 0.07)',
					backdropFilter: 'blur(18px)'
				}
			}
		},
		MuiCard: {
			styleOverrides: {
				root: {
					borderRadius: 24,
					background: 'rgba(253, 250, 244, 0.96)',
					border: '1px solid rgba(167, 145, 102, 0.14)',
					boxShadow: '0 16px 40px rgba(112, 93, 60, 0.07)'
				}
			}
		},
		MuiButton: {
			styleOverrides: {
				root: {
					minHeight: 40,
					borderRadius: 14,
					paddingInline: 16
				},
				contained: {
					backgroundColor: '#9f8550',
					boxShadow: 'none',
					'&:hover': {
						backgroundColor: '#8f7648',
						boxShadow: 'none'
					}
				},
				outlined: {
					borderColor: 'rgba(167, 145, 102, 0.28)',
					backgroundColor: 'rgba(250, 246, 237, 0.9)'
				},
				text: {
					color: '#6f5d3e'
				}
			}
		},
		MuiChip: {
			styleOverrides: {
				root: {
					borderRadius: 999,
					fontWeight: 650
				}
			}
		},
		MuiTableCell: {
			styleOverrides: {
				head: {
					color: '#8a7a63',
					fontWeight: 700,
					backgroundColor: 'rgba(249, 244, 233, 0.92)'
				},
				root: {
					borderBottom: '1px solid rgba(231, 222, 203, 0.92)',
					verticalAlign: 'top'
				}
			}
		},
		MuiDialog: {
			styleOverrides: {
				paper: {
					borderRadius: 24,
					border: '1px solid rgba(167, 145, 102, 0.16)',
					boxShadow: '0 24px 64px rgba(112, 93, 60, 0.12)'
				}
			}
		},
		MuiDrawer: {
			styleOverrides: {
				paper: {
					background: 'rgba(252, 249, 242, 0.98)',
					borderLeft: '1px solid rgba(167, 145, 102, 0.14)'
				}
			}
		}
	}
})
