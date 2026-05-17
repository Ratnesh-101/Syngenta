import Header from './Header';
import ToastContainer from './ToastContainer';
import { useOfflineQueue } from '../hooks/useOfflineQueue';

interface LayoutProps {
  children: React.ReactNode;
  title?: string;
  showBack?: boolean;
}

export default function Layout({ children, title, showBack }: LayoutProps) {
  const { toasts, dismissToast } = useOfflineQueue();

  return (
    <div className="min-h-screen bg-forest-50">
      <Header title={title} showBack={showBack} />
      <main className="max-w-2xl mx-auto px-4 py-5 pb-10">
        {children}
      </main>
      <ToastContainer toasts={toasts} onDismiss={dismissToast} />
    </div>
  );
}
