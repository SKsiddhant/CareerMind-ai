import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Search, 
  FileText, 
  Mic2, 
  DollarSign,
  TrendingUp
} from 'lucide-react';
import styles from './Sidebar.module.css';

const Sidebar: React.FC = () => {
  const navItems = [
    { path: '/', icon: <LayoutDashboard size={20} />, label: 'Dashboard' },
    { path: '/intelligence', icon: <Search size={20} />, label: 'Job Intelligence' },
    { path: '/tailor', icon: <FileText size={20} />, label: 'Resume Tailor' },
    { path: '/interview', icon: <Mic2 size={20} />, label: 'Interview Coach' },
    { path: '/negotiate', icon: <DollarSign size={20} />, label: 'Salary Negotiator' },
  ];

  return (
    <div className={styles.sidebar}>
      <div className={styles.logo}>
        <TrendingUp className={styles.logoIcon} />
        <span className="text-gradient">CareerMind AI</span>
      </div>
      <nav className={styles.nav}>
        {navItems.map((item) => (
          <NavLink 
            key={item.path} 
            to={item.path} 
            className={({ isActive }) => 
              `${styles.navItem} ${isActive ? styles.active : ''}`
            }
          >
            {item.icon}
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>
      <div className={styles.footer}>
        <div className={styles.status}>
          <div className={styles.pulse}></div>
          <span>System: GOATed</span>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
