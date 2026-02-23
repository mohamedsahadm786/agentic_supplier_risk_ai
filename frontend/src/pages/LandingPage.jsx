import { useState } from 'react';
import Navbar          from '../components/landing/Navbar';
import HeroSection     from '../components/landing/HeroSection';
import HowItWorks      from '../components/landing/HowItWorks';
import FeaturesSection from '../components/landing/FeaturesSection';
import PricingSection  from '../components/landing/PricingSection';
import CreatorSection  from '../components/landing/CreatorSection';
import Footer          from '../components/landing/Footer';
import LoginModal      from '../components/auth/LoginModal';
import SignupModal     from '../components/auth/SignupModal';

export default function LandingPage() {
  // Which modal is open: null | 'login' | 'signup'
  const [modal, setModal] = useState(null);

  const openLogin  = () => setModal('login');
  const openSignup = () => setModal('signup');
  const closeModal = () => setModal(null);

  return (
    <div className="page-bg">
      {/* Fixed top navigation */}
      <Navbar onLoginClick={openLogin} onSignupClick={openSignup} />

      {/* Page sections */}
      <HeroSection     onGetStarted={openSignup} />
      <HowItWorks />
      <FeaturesSection />
      <PricingSection  onGetStarted={openSignup} />
      <CreatorSection />
      <Footer />

      {/* Modals — rendered on top of everything */}
      {modal === 'login' && (
        <LoginModal
          onClose={closeModal}
          onSwitchToSignup={() => setModal('signup')}
        />
      )}
      {modal === 'signup' && (
        <SignupModal
          onClose={closeModal}
          onSwitchToLogin={() => setModal('login')}
        />
      )}
    </div>
  );
}