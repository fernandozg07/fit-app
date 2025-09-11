import React from 'react';

const Card = ({ 
  children, 
  className = '', 
  hover = false, 
  padding = 'p-6',
  shadow = 'shadow-sm'
}) => {
  const baseClasses = `bg-white rounded-xl border ${shadow} ${padding}`;
  const hoverClasses = hover ? 'hover:shadow-lg transition-all duration-300 cursor-pointer' : '';
  
  return (
    <div className={`${baseClasses} ${hoverClasses} ${className}`}>
      {children}
    </div>
  );
};

export default Card;