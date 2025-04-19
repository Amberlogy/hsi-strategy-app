import React from 'react';

export default function NotFound() {
  return (
    React.createElement('div', null,
      React.createElement('h1', null, '404'),
      React.createElement('p', null, '找不到頁面'),
      React.createElement('a', { href: '/' }, '返回首頁')
    )
  );
} 