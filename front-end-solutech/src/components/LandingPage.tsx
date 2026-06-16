/**
 * =============================================================================
 * LANDING PAGE SOLUTECH v2.0
 * Page d'accueil publique présentant la plateforme aux établissements scolaires
 * Optimisée pour mobile, réseaux 3G/4G, et contexte congolais
 * =============================================================================
 */

import { useState } from 'react';
import { Link } from 'react-router-dom';
import {
  School,
  WifiOff,
  Shield,
  Smartphone,
  Users,
  GraduationCap,
  BookOpen,
  BarChart3,
  CheckCircle2,
  ArrowRight,
  Menu,
  X,
  Globe,
  Lock,
  Award,
  Mail,
  Phone,
  MapPin,
} from 'lucide-react';

export function LandingPage() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <div className="min-h-screen bg-base-100">
      {/* Navigation */}
      <nav className="sticky top-0 z-50 bg-base-100/95 backdrop-blur border-b border-base-300">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-2">
              <div className="w-10 h-10 bg-primary rounded-xl flex items-center justify-center">
                <School className="w-5 h-5 text-primary-content" />
              </div>
              <span className="font-bold text-lg">SOLUTECH</span>
            </div>

            {/* Desktop menu */}
            <div className="hidden md:flex items-center gap-6">
              <a href="#features" className="text-sm hover:text-primary transition-colors">Fonctionnalités</a>
              <a href="#benefits" className="text-sm hover:text-primary transition-colors">Avantages</a>
              <a href="#conformite" className="text-sm hover:text-primary transition-colors">Conformité</a>
              <a href="#contact" className="text-sm hover:text-primary transition-colors">Contact</a>
              <Link to="/login" className="btn btn-primary btn-sm">
                Connexion
              </Link>
            </div>

            {/* Mobile menu button */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden btn btn-ghost btn-sm btn-circle"
              aria-label="Menu"
            >
              {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>

        {/* Mobile menu */}
        {mobileMenuOpen && (
          <div className="md:hidden border-t border-base-300 bg-base-100">
            <div className="px-4 py-3 space-y-2">
              <a href="#features" onClick={() => setMobileMenuOpen(false)} className="block py-2 text-sm">Fonctionnalités</a>
              <a href="#benefits" onClick={() => setMobileMenuOpen(false)} className="block py-2 text-sm">Avantages</a>
              <a href="#conformite" onClick={() => setMobileMenuOpen(false)} className="block py-2 text-sm">Conformité</a>
              <a href="#contact" onClick={() => setMobileMenuOpen(false)} className="block py-2 text-sm">Contact</a>
              <Link to="/login" onClick={() => setMobileMenuOpen(false)} className="btn btn-primary btn-sm w-full">
                Connexion
              </Link>
            </div>
          </div>
        )}
      </nav>

      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-primary/10 via-base-100 to-secondary/10">
        <div className="max-w-7xl mx-auto px-4 py-16 md:py-24">
          <div className="grid md:grid-cols-2 gap-8 items-center">
            <div>
              <div className="badge badge-primary badge-sm mb-4">Nouveau · Mode Hors-Ligne</div>
              <h1 className="text-3xl md:text-5xl font-bold leading-tight">
                La plateforme de gestion scolaire adaptée au{' '}
                <span className="text-primary">Congo</span>
              </h1>
              <p className="mt-4 text-base md:text-lg text-base-content/70">
                SOLUTECH v2.0 est conçue pour les établissements congolais : préscolaire, primaire, 
                secondaire et technique. Fonctionne même sans connexion internet.
              </p>
              <div className="mt-6 flex flex-col sm:flex-row gap-3">
                <Link to="/login" className="btn btn-primary btn-md gap-2">
                  Essayer la démo
                  <ArrowRight className="w-4 h-4" />
                </Link>
                <a href="#features" className="btn btn-outline btn-md">
                  Découvrir les fonctionnalités
                </a>
              </div>
              <div className="mt-6 flex items-center gap-4 text-xs text-base-content/50">
                <div className="flex items-center gap-1">
                  <CheckCircle2 className="w-3.5 h-3.5 text-success" />
                  <span>Conforme MEPSA/MESRSIT</span>
                </div>
                <div className="flex items-center gap-1">
                  <CheckCircle2 className="w-3.5 h-3.5 text-success" />
                  <span>Données sécurisées</span>
                </div>
              </div>
            </div>
            <div className="relative">
              <div className="card bg-base-100 shadow-2xl border border-base-300">
                <div className="card-body p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
                        <School className="w-4 h-4 text-primary-content" />
                      </div>
                      <div>
                        <p className="text-xs font-bold">École Primaire Marien Ngouabi</p>
                        <p className="text-[10px] text-base-content/50">Brazzaville</p>
                      </div>
                    </div>
                    <div className="badge badge-success badge-xs">En ligne</div>
                  </div>
                  <div className="grid grid-cols-2 gap-2">
                    <div className="bg-base-200 rounded-lg p-3 text-center">
                      <p className="text-xl font-bold text-primary">342</p>
                      <p className="text-[10px] text-base-content/50">Élèves</p>
                    </div>
                    <div className="bg-base-200 rounded-lg p-3 text-center">
                      <p className="text-xl font-bold text-secondary">18</p>
                      <p className="text-[10px] text-base-content/50">Enseignants</p>
                    </div>
                    <div className="bg-base-200 rounded-lg p-3 text-center">
                      <p className="text-xl font-bold text-success">94%</p>
                      <p className="text-[10px] text-base-content/50">Présence</p>
                    </div>
                    <div className="bg-base-200 rounded-lg p-3 text-center">
                      <p className="text-xl font-bold text-warning">12.4</p>
                      <p className="text-[10px] text-base-content/50">Moyenne</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-12 bg-base-200">
        <div className="max-w-7xl mx-auto px-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <StatItem number="500+" label="Établissements" />
            <StatItem number="50 000+" label="Élèves inscrits" />
            <StatItem number="99.9%" label="Disponibilité" />
            <StatItem number="24/7" label="Support" />
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-16 md:py-24">
        <div className="max-w-7xl mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-2xl md:text-3xl font-bold">Fonctionnalités complètes</h2>
            <p className="mt-2 text-base-content/70">Tout ce dont vous avez besoin pour gérer votre établissement</p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            <FeatureCard
              icon={<WifiOff className="w-6 h-6" />}
              title="Mode Hors-Ligne"
              description="Travaillez sans connexion. Les données se synchronisent automatiquement lors du retour en ligne."
              color="bg-amber-500"
            />
            <FeatureCard
              icon={<Shield className="w-6 h-6" />}
              title="Sécurité renforcée"
              description="Chiffrement des données sensibles, contrôle d'accès par rôle, conformité Constitution art. 29."
              color="bg-emerald-500"
            />
            <FeatureCard
              icon={<Smartphone className="w-6 h-6" />}
              title="Mobile First"
              description="Optimisé pour Android, Chrome et Opera Mini. Interface tactile adaptée aux smartphones."
              color="bg-blue-500"
            />
            <FeatureCard
              icon={<Users className="w-6 h-6" />}
              title="Gestion des élèves"
              description="Inscriptions, dossiers complets, suivi individualisé, historique scolaire."
              color="bg-violet-500"
            />
            <FeatureCard
              icon={<BookOpen className="w-6 h-6" />}
              title="Notes et bulletins"
              description="Saisie des notes, calcul automatique des moyennes, génération des bulletins."
              color="bg-pink-500"
            />
            <FeatureCard
              icon={<BarChart3 className="w-6 h-6" />}
              title="Statistiques"
              description="Tableaux de bord, indicateurs de performance, rapports pour le MEPSA."
              color="bg-cyan-500"
            />
          </div>
        </div>
      </section>

      {/* Benefits by Role */}
      <section id="benefits" className="py-16 md:py-24 bg-base-200">
        <div className="max-w-7xl mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-2xl md:text-3xl font-bold">Avantages par profil</h2>
            <p className="mt-2 text-base-content/70">Une solution adaptée à chaque utilisateur</p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
            <BenefitCard
              icon={<GraduationCap className="w-8 h-8" />}
              role="Directeurs"
              benefits={[
                'Vue d\'ensemble en temps réel',
                'Rapports automatiques MEPSA',
                'Gestion du personnel',
                'Alertes et notifications',
              ]}
            />
            <BenefitCard
              icon={<BookOpen className="w-8 h-8" />}
              role="Enseignants"
              benefits={[
                'Saisie rapide des notes',
                'Feuille d\'appel numérique',
                'Suivi individuel des élèves',
                'Génération de bulletins',
              ]}
            />
            <BenefitCard
              icon={<Users className="w-8 h-8" />}
              role="Élèves"
              benefits={[
                'Consultation des notes',
                'Emploi du temps',
                'Historique scolaire',
                'Documents téléchargeables',
              ]}
            />
            <BenefitCard
              icon={<Shield className="w-8 h-8" />}
              role="Parents"
              benefits={[
                'Suivi des résultats',
                'Notifications d\'absence',
                'Communication école-famille',
                'Accès sécurisé',
              ]}
            />
          </div>
        </div>
      </section>

      {/* Conformité Section */}
      <section id="conformite" className="py-16 md:py-24">
        <div className="max-w-7xl mx-auto px-4">
          <div className="grid md:grid-cols-2 gap-8 items-center">
            <div>
              <h2 className="text-2xl md:text-3xl font-bold">Conformité et sécurité</h2>
              <p className="mt-4 text-base-content/70">
                SOLUTECH respecte strictement la réglementation congolaise en matière de protection 
                des données personnelles et les directives du Ministère de l'Enseignement.
              </p>
              <div className="mt-6 space-y-3">
                <ComplianceItem
                  icon={<Lock className="w-5 h-5" />}
                  title="Constitution art. 29"
                  description="Protection de la vie privée et des données personnelles"
                />
                <ComplianceItem
                  icon={<Globe className="w-5 h-5" />}
                  title="Hébergement africain"
                  description="Données stockées sur le continent conformément aux accords de transfert"
                />
                <ComplianceItem
                  icon={<Award className="w-5 h-5" />}
                  title="Directives MEPSA/MESRSIT"
                  description="Structure officielle du système éducatif congolais respectée"
                />
              </div>
            </div>
            <div className="card bg-gradient-to-br from-primary/10 to-secondary/10 border border-primary/20">
              <div className="card-body p-6">
                <h3 className="font-bold text-lg mb-4">Engagements SOLUTECH</h3>
                <ul className="space-y-3 text-sm">
                  <li className="flex items-start gap-2">
                    <CheckCircle2 className="w-5 h-5 text-success shrink-0 mt-0.5" />
                    <span>Chiffrement AES-256 des données sensibles des élèves mineurs</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle2 className="w-5 h-5 text-success shrink-0 mt-0.5" />
                    <span>Contrôle d'accès parental avec journal d'audit</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle2 className="w-5 h-5 text-success shrink-0 mt-0.5" />
                    <span>Serveurs certifiés ISO 27001 situés en Afrique</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle2 className="w-5 h-5 text-success shrink-0 mt-0.5" />
                    <span>Sauvegardes automatiques quotidiennes</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle2 className="w-5 h-5 text-success shrink-0 mt-0.5" />
                    <span>Support technique basé à Brazzaville</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 bg-primary text-primary-content">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <h2 className="text-2xl md:text-3xl font-bold">Prêt à digitaliser votre établissement ?</h2>
          <p className="mt-4 text-primary-content/80">
            Rejoignez les centaines d'écoles congolaises qui font confiance à SOLUTECH pour 
            la gestion de leurs activités scolaires.
          </p>
          <div className="mt-8 flex flex-col sm:flex-row gap-3 justify-center">
            <Link to="/login" className="btn btn-secondary btn-md">
              Accéder à la démo
            </Link>
            <a href="#contact" className="btn btn-outline btn-md border-primary-content text-primary-content hover:bg-primary-content hover:text-primary">
              Contacter l'équipe
            </a>
          </div>
        </div>
      </section>

      {/* Contact Section */}
      <section id="contact" className="py-16 md:py-24 bg-base-200">
        <div className="max-w-7xl mx-auto px-4">
          <div className="grid md:grid-cols-2 gap-8">
            <div>
              <h2 className="text-2xl md:text-3xl font-bold">Contactez-nous</h2>
              <p className="mt-2 text-base-content/70">
                Notre équipe basée à Brazzaville est disponible pour répondre à vos questions 
                et vous accompagner dans la mise en place de SOLUTECH.
              </p>
              <div className="mt-6 space-y-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center">
                    <Mail className="w-5 h-5 text-primary" />
                  </div>
                  <div>
                    <p className="text-xs text-base-content/50">Email</p>
                    <p className="text-sm font-medium">contact@solutech.cg</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center">
                    <Phone className="w-5 h-5 text-primary" />
                  </div>
                  <div>
                    <p className="text-xs text-base-content/50">Téléphone</p>
                    <p className="text-sm font-medium">+242 06 XXX XX XX</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center">
                    <MapPin className="w-5 h-5 text-primary" />
                  </div>
                  <div>
                    <p className="text-xs text-base-content/50">Adresse</p>
                    <p className="text-sm font-medium">Brazzaville, République du Congo</p>
                  </div>
                </div>
              </div>
            </div>
            <div className="card bg-base-100 shadow-sm">
              <div className="card-body p-6">
                <h3 className="font-bold text-lg mb-4">Demande de démonstration</h3>
                <form className="space-y-3" onSubmit={(e) => e.preventDefault()}>
                  <div className="form-control">
                    <label className="label label-text text-xs">Nom de l'établissement</label>
                    <input type="text" className="input input-bordered input-sm w-full" placeholder="Ex: École Primaire..." />
                  </div>
                  <div className="form-control">
                    <label className="label label-text text-xs">Votre nom</label>
                    <input type="text" className="input input-bordered input-sm w-full" placeholder="Nom complet" />
                  </div>
                  <div className="form-control">
                    <label className="label label-text text-xs">Email</label>
                    <input type="email" className="input input-bordered input-sm w-full" placeholder="votre@email.cg" />
                  </div>
                  <div className="form-control">
                    <label className="label label-text text-xs">Téléphone</label>
                    <input type="tel" className="input input-bordered input-sm w-full" placeholder="+242 0X XX XX XX" />
                  </div>
                  <button type="submit" className="btn btn-primary btn-sm w-full">
                    Envoyer la demande
                  </button>
                </form>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-base-300 py-8">
        <div className="max-w-7xl mx-auto px-4">
          <div className="grid md:grid-cols-4 gap-6">
            <div>
              <div className="flex items-center gap-2 mb-3">
                <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
                  <School className="w-4 h-4 text-primary-content" />
                </div>
                <span className="font-bold">SOLUTECH</span>
              </div>
              <p className="text-xs text-base-content/60">
                Plateforme de gestion scolaire pour la République du Congo.
              </p>
            </div>
            <div>
              <h4 className="font-bold text-sm mb-3">Produit</h4>
              <ul className="space-y-1 text-xs text-base-content/60">
                <li><a href="#features" className="hover:text-primary">Fonctionnalités</a></li>
                <li><a href="#benefits" className="hover:text-primary">Avantages</a></li>
                <li><a href="#conformite" className="hover:text-primary">Sécurité</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-bold text-sm mb-3">Légal</h4>
              <ul className="space-y-1 text-xs text-base-content/60">
                <li>Conditions d'utilisation</li>
                <li>Politique de confidentialité</li>
                <li>Mentions légales</li>
              </ul>
            </div>
            <div>
              <h4 className="font-bold text-sm mb-3">Support</h4>
              <ul className="space-y-1 text-xs text-base-content/60">
                <li>Documentation</li>
                <li>FAQ</li>
                <li>Contact</li>
              </ul>
            </div>
          </div>
          <div className="border-t border-base-400 mt-6 pt-6 text-center text-xs text-base-content/40">
            <p>© 2024 SOLUTECH Congo. Tous droits réservés.</p>
            <p className="mt-1">
              Conforme à la Constitution de la République du Congo, art. 29 · 
              Respect des directives MEPSA/MESRSIT
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}

function StatItem({ number, label }: { number: string; label: string }) {
  return (
    <div className="text-center">
      <p className="text-2xl md:text-3xl font-bold text-primary">{number}</p>
      <p className="text-xs text-base-content/60 mt-1">{label}</p>
    </div>
  );
}

function FeatureCard({
  icon,
  title,
  description,
  color,
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
  color: string;
}) {
  return (
    <div className="card bg-base-100 shadow-sm hover:shadow-md transition-shadow">
      <div className="card-body p-5">
        <div className={`w-12 h-12 ${color} rounded-xl flex items-center justify-center text-white mb-3`}>
          {icon}
        </div>
        <h3 className="font-bold text-sm mb-2">{title}</h3>
        <p className="text-xs text-base-content/70">{description}</p>
      </div>
    </div>
  );
}

function BenefitCard({
  icon,
  role,
  benefits,
}: {
  icon: React.ReactNode;
  role: string;
  benefits: string[];
}) {
  return (
    <div className="card bg-base-100 shadow-sm">
      <div className="card-body p-5">
        <div className="w-12 h-12 bg-primary/10 rounded-xl flex items-center justify-center text-primary mb-3">
          {icon}
        </div>
        <h3 className="font-bold text-sm mb-3">{role}</h3>
        <ul className="space-y-2">
          {benefits.map((b, i) => (
            <li key={i} className="flex items-start gap-2 text-xs text-base-content/70">
              <CheckCircle2 className="w-3.5 h-3.5 text-success shrink-0 mt-0.5" />
              <span>{b}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

function ComplianceItem({
  icon,
  title,
  description,
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
}) {
  return (
    <div className="flex items-start gap-3">
      <div className="w-8 h-8 bg-primary/10 rounded-lg flex items-center justify-center shrink-0">
        {icon}
      </div>
      <div>
        <h4 className="font-bold text-sm">{title}</h4>
        <p className="text-xs text-base-content/60">{description}</p>
      </div>
    </div>
  );
}
