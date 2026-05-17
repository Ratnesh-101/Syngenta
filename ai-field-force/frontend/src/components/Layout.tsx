import Header from './Header';
import ToastContainer from './ToastContainer';
import { useOfflineQueue } from '../hooks/useOfflineQueue';

interface LayoutProps {
  children: React.ReactNode;
  title?: string;
  showBack?: boolean;
  /** Optional: pages that should stay narrow on desktop (e.g. forms, grower detail).
   *  Defaults to false — most pages get the wide desktop layout. */
  narrow?: boolean;
}

export default function Layout({ children, title, showBack, narrow = false }: LayoutProps) {
  const { toasts, dismissToast } = useOfflineQueue();

  // Mobile: always max-w-2xl. Desktop: wide unless narrow=true.
  const mainClasses = narrow
    ? 'max-w-2xl mx-auto px-4 py-5 pb-10'
    : 'max-w-2xl md:max-w-5xl lg:max-w-6xl mx-auto px-4 md:px-8 py-5 md:py-8 pb-10';

  return (
    <div className="min-h-screen bg-forest-50">
      <Header title={title} showBack={showBack} />
      <main className={mainClasses}>
        {children}
      </main>
      <ToastContainer toasts={toasts} onDismiss={dismissToast} />
    </div>
  );
}