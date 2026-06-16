/**
 * =============================================================================
 * HOOK D'ENREGISTREMENT DU SERVICE WORKER
 * Gestion de l'installation et des mises à jour de la PWA
 * =============================================================================
 */

import { useEffect, useState } from 'react';

export function useServiceWorker() {
  const [isReady, setIsReady] = useState(false);
  const [updateAvailable, setUpdateAvailable] = useState(false);
  const [registration, setRegistration] = useState<ServiceWorkerRegistration | null>(null);

  useEffect(() => {
    if (!('serviceWorker' in navigator)) {
      console.warn('[SW] Service Worker non supporté');
      return;
    }

    const registerSW = async () => {
      try {
        const reg = await navigator.serviceWorker.register('/sw.js', {
          scope: '/',
        });

        setRegistration(reg);

        // Vérifier si le SW est prêt
        if (reg.active) {
          setIsReady(true);
          console.log('[SW] Service Worker actif');
        }

        // Écouter les mises à jour
        reg.addEventListener('updatefound', () => {
          const newWorker = reg.installing;
          if (!newWorker) return;

          newWorker.addEventListener('statechange', () => {
            if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
              // Nouvelle version disponible
              setUpdateAvailable(true);
              console.log('[SW] Nouvelle version disponible');
            }
          });
        });

        // Écouter les messages du SW
        navigator.serviceWorker.addEventListener('message', (event) => {
          if (event.data.type === 'CACHE_UPDATED') {
            console.log('[SW] Cache mis à jour');
          }
        });
      } catch (error) {
        console.error('[SW] Erreur d\'enregistrement:', error);
      }
    };

    registerSW();
  }, []);

  /** Mettre à jour vers la nouvelle version */
  const update = async () => {
    if (!registration?.waiting) return;
    
    registration.addEventListener('updatefound', () => {
      const newWorker = registration.installing;
      if (!newWorker) return;

      newWorker.addEventListener('statechange', () => {
        if (newWorker.state === 'activated' && navigator.serviceWorker.controller) {
          window.location.reload();
        }
      });
    });

    registration.waiting.postMessage({ type: 'SKIP_WAITING' });
  };

  /** Désinscrire le service worker */
  const unregister = async () => {
    if (!registration) return;
    await registration.unregister();
    console.log('[SW] Service Worker désinscrit');
  };

  return {
    isReady,
    updateAvailable,
    update,
    unregister,
  };
}
