import React from 'react';

interface LayoutProps {
  children: React.ReactNode;
  className?: string;
}

export const Layout: React.FC<LayoutProps> = ({ children, className = '' }) => {
  return (
    <div className={`min-h-screen bg-gradient-to-br from-orange-50 to-red-50 ${className}`}>
      <div className="container mx-auto px-4 py-6 max-w-md">
        {children}
      </div>
    </div>
  );
};