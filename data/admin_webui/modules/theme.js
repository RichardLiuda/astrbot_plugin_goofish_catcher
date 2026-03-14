import { createTheme } from './deps.js'

function createAppTheme(mode) {
	const isDark = mode === 'dark'
	return createTheme({
		palette: {
			mode,
			primary: { main: isDark ? '#d4b06f' : '#9f8550' },
			secondary: { main: isDark ? '#b79b65' : '#7d6942' },
			success: { main: '#22c55e' },
			warning: { main: '#f59e0b' },
			error: { main: '#ef4444' },
			background: {
				default: isDark ? '#16120d' : '#f6f1e7',
				paper: isDark ? '#211b14' : '#fdfaf4'
			},
			text: {
				primary: isDark ? '#f4ead8' : '#30261a',
				secondary: isDark ? '#b8ab95' : '#7b6d5a'
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
						background: isDark
							? 'rgba(31, 26, 20, 0.9)'
							: 'rgba(253, 250, 244, 0.9)',
						color: isDark ? '#f4ead8' : '#30261a',
						border: `1px solid ${isDark ? 'rgba(212, 176, 111, 0.16)' : 'rgba(167, 145, 102, 0.16)'}`,
						boxShadow: isDark
							? '0 12px 30px rgba(0, 0, 0, 0.28)'
							: '0 12px 30px rgba(112, 93, 60, 0.07)',
						backdropFilter: 'blur(18px)'
					}
				}
			},
			MuiCard: {
				styleOverrides: {
					root: {
						borderRadius: 24,
						background: isDark
							? 'rgba(33, 27, 20, 0.96)'
							: 'rgba(253, 250, 244, 0.96)',
						border: `1px solid ${isDark ? 'rgba(212, 176, 111, 0.12)' : 'rgba(167, 145, 102, 0.14)'}`,
						boxShadow: isDark
							? '0 18px 40px rgba(0, 0, 0, 0.3)'
							: '0 16px 40px rgba(112, 93, 60, 0.07)'
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
						backgroundColor: isDark ? '#c9a463' : '#9f8550',
						boxShadow: 'none',
						'&:hover': {
							backgroundColor: isDark ? '#b89253' : '#8f7648',
							boxShadow: 'none'
						}
					},
					outlined: {
						borderColor: isDark
							? 'rgba(212, 176, 111, 0.28)'
							: 'rgba(167, 145, 102, 0.28)',
						backgroundColor: isDark
							? 'rgba(43, 36, 28, 0.9)'
							: 'rgba(250, 246, 237, 0.9)'
					},
					text: {
						color: isDark ? '#d2bc94' : '#6f5d3e'
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
						color: isDark ? '#c9b593' : '#8a7a63',
						fontWeight: 700,
						backgroundColor: isDark
							? 'rgba(39, 33, 25, 0.92)'
							: 'rgba(249, 244, 233, 0.92)'
					},
					root: {
						borderBottom: `1px solid ${isDark ? 'rgba(91, 76, 56, 0.92)' : 'rgba(231, 222, 203, 0.92)'}`,
						verticalAlign: 'top'
					}
				}
			},
			MuiDialog: {
				styleOverrides: {
					paper: {
						borderRadius: 24,
						border: `1px solid ${isDark ? 'rgba(212, 176, 111, 0.16)' : 'rgba(167, 145, 102, 0.16)'}`,
						boxShadow: isDark
							? '0 24px 64px rgba(0, 0, 0, 0.42)'
							: '0 24px 64px rgba(112, 93, 60, 0.12)'
					}
				}
			},
			MuiDrawer: {
				styleOverrides: {
					paper: {
						background: isDark
							? 'rgba(24, 20, 15, 0.98)'
							: 'rgba(252, 249, 242, 0.98)',
						borderLeft: `1px solid ${isDark ? 'rgba(212, 176, 111, 0.14)' : 'rgba(167, 145, 102, 0.14)'}`
					}
				}
			}
		}
	})
}

export const lightTheme = createAppTheme('light')
export const darkTheme = createAppTheme('dark')
