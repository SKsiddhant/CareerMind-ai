import React from 'react';
import Sidebar from './Sidebar';
import styles from './MainLayout.module.css';

interface MainLayoutProps {
  children: React.ReactNode;
}

const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  return (
    <div className={styles.layout}>
      <Sidebar />
      <main className={styles.content}>
        <div className={styles.container}>
          {children}
        </div>
      </main>
    </div>
  );
};

export default MainLayout;
