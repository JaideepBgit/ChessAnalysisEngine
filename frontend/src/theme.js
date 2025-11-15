// Theme configuration for the Chess Engine Interface

export const lightTheme = {
  // Primary Colors
  '--primary-purple': '#633394',
  '--secondary-purple': '#967CB2',
  '--dark-purple': '#3B1C55',
  '--brown-accent': '#61382E',
  
  // Background Colors
  '--bg-primary': '#FBFAFA',
  '--bg-secondary': '#FFFFFF',
  '--bg-tertiary': '#F5F5F5',
  '--bg-hover': '#EEEEEE',
  
  // Text Colors
  '--text-primary': '#3B1C55',
  '--text-secondary': '#61382E',
  '--text-muted': '#967CB2',
  
  // Border Colors
  '--border-primary': '#E0E0E0',
  '--border-secondary': '#D0D0D0',
  '--border-accent': '#633394',
  
  // Accent Colors
  '--accent-primary': '#633394',
  '--accent-secondary': '#967CB2',
  '--accent-tertiary': '#967CB2',
  '--accent-warning': '#d4a574',
  '--accent-gradient': 'linear-gradient(135deg, #633394 0%, #967CB2 100%)',
  
  // Status Colors
  '--success': '#4caf50',
  '--warning': '#ff9800',
  '--error': '#f44336',
  
  // Shadows
  '--shadow-sm': '0 2px 8px rgba(99, 51, 148, 0.1)',
  '--shadow-md': '0 4px 16px rgba(99, 51, 148, 0.15)',
  '--shadow-lg': '0 8px 32px rgba(99, 51, 148, 0.2)',
  '--shadow-accent': '0 4px 20px rgba(99, 51, 148, 0.25)',
  '--shadow-glow': '0 0 20px rgba(99, 51, 148, 0.2)',
};

export const darkTheme = {
  // Background Colors - Dark Base
  '--bg-primary': '#0a0a0f',
  '--bg-secondary': '#13131a',
  '--bg-tertiary': '#1c1c26',
  '--bg-hover': '#252532',
  
  // Accent Colors - Muted Purple Theme
  '--accent-primary': '#8b7fc8',
  '--accent-secondary': '#6b5fb0',
  '--accent-tertiary': '#9d8fd4',
  '--accent-warning': '#d4a574',
  '--accent-gradient': 'linear-gradient(135deg, #8b7fc8 0%, #6b5fb0 100%)',
  
  // Text Colors
  '--text-primary': '#e4e4e7',
  '--text-secondary': '#a1a1aa',
  '--text-muted': '#71717a',
  
  // Border Colors
  '--border-primary': '#27272a',
  '--border-secondary': '#3f3f46',
  '--border-accent': '#8b7fc8',
  
  // Status Colors
  '--success': '#6ee7b7',
  '--warning': '#fbbf24',
  '--error': '#f87171',
  
  // Shadows
  '--shadow-sm': '0 2px 8px rgba(0, 0, 0, 0.5)',
  '--shadow-md': '0 4px 16px rgba(0, 0, 0, 0.6)',
  '--shadow-lg': '0 8px 32px rgba(0, 0, 0, 0.7)',
  '--shadow-accent': '0 4px 20px rgba(139, 127, 200, 0.3)',
  '--shadow-glow': '0 0 20px rgba(139, 127, 200, 0.25)',
};

export const applyTheme = (theme) => {
  const root = document.documentElement;
  Object.keys(theme).forEach(key => {
    root.style.setProperty(key, theme[key]);
  });
};
