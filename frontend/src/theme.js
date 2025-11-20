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
  // Background Colors - Warm Beige/Tan Base
  '--bg-primary': '#584439',
  '--bg-secondary': '#6b5442',
  '--bg-tertiary': '#82654d',
  '--bg-hover': '#9c7a5a',
  
  // Accent Colors - Lighter Warm Beige/Tan Palette
  '--accent-primary': '#e8ddd0',
  '--accent-secondary': '#f5f1eb',
  '--accent-tertiary': '#faf8f5',
  '--accent-warning': '#cba688',
  '--accent-gradient': 'linear-gradient(135deg, #e8ddd0 0%, #d9c7b3 100%)',
  
  // Sage Accent Colors
  '--sage-primary': '#aeb6ae',
  '--sage-secondary': '#d2d6d2',
  '--sage-light': '#e8eae8',
  
  // Text Colors - White/Light for high contrast
  '--text-primary': '#ffffff',
  '--text-secondary': '#f5f1eb',
  '--text-muted': '#d9c7b3',
  
  // Border Colors
  '--border-primary': '#9c7a5a',
  '--border-secondary': '#82654d',
  '--border-accent': '#e8ddd0',
  
  // Status Colors
  '--success': '#aeb6ae',
  '--warning': '#e8ddd0',
  '--error': '#ff6b6b',
  
  // Shadows
  '--shadow-sm': '0 2px 8px rgba(88, 68, 57, 0.5)',
  '--shadow-md': '0 4px 16px rgba(88, 68, 57, 0.6)',
  '--shadow-lg': '0 8px 32px rgba(88, 68, 57, 0.7)',
  '--shadow-accent': '0 4px 20px rgba(232, 221, 208, 0.4)',
  '--shadow-glow': '0 0 20px rgba(232, 221, 208, 0.3)',
};

export const applyTheme = (theme) => {
  const root = document.documentElement;
  Object.keys(theme).forEach(key => {
    root.style.setProperty(key, theme[key]);
  });
};
