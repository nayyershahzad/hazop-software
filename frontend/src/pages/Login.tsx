import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';

export const Login = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [organizationName, setOrganizationName] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [passwordStrength, setPasswordStrength] = useState<{
    hasMinLength: boolean;
    hasUppercase: boolean;
    hasLowercase: boolean;
    hasNumber: boolean;
  }>({
    hasMinLength: false,
    hasUppercase: false,
    hasLowercase: false,
    hasNumber: false
  });

  const { login, register } = useAuthStore();
  const navigate = useNavigate();

  const checkPasswordStrength = (pwd: string) => {
    setPasswordStrength({
      hasMinLength: pwd.length >= 8,
      hasUppercase: /[A-Z]/.test(pwd),
      hasLowercase: /[a-z]/.test(pwd),
      hasNumber: /\d/.test(pwd)
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (isLogin) {
        await login(email, password);
      } else {
        await register(email, password, fullName, organizationName);
      }
      navigate('/studies');
    } catch (err: any) {
      const errorDetail = err.response?.data?.detail;
      if (typeof errorDetail === 'string') {
        setError(errorDetail);
      } else if (Array.isArray(errorDetail)) {
        // Handle Pydantic validation errors
        const errors = errorDetail.map((e: any) => e.msg).join(', ');
        setError(errors);
      } else {
        setError('Authentication failed. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const isPasswordValid = !isLogin || (
    passwordStrength.hasMinLength &&
    passwordStrength.hasUppercase &&
    passwordStrength.hasLowercase &&
    passwordStrength.hasNumber
  );

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="bg-white p-8 rounded-xl shadow-lg w-full max-w-md">
        <div className="text-center mb-6">
          <h1 className="text-3xl font-bold mb-2 text-gray-800">
            HAZOP Analysis System
          </h1>
          <p className="text-gray-600">
            {isLogin ? 'Welcome back! Sign in to your account' : 'Create your HAZOP workspace'}
          </p>
        </div>

        {!isLogin && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
            <h3 className="font-semibold text-blue-900 mb-2 flex items-center">
              <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
              </svg>
              Sign Up Guide
            </h3>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>• Enter your work email address</li>
              <li>• Create a strong password (see requirements below)</li>
              <li>• Provide your full name</li>
              <li>• Name your organization/company</li>
              <li>• You'll be the organization owner with full access</li>
            </ul>
          </div>
        )}

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4 flex items-start">
            <svg className="w-5 h-5 mr-2 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {!isLogin && (
            <>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Full Name *
                </label>
                <input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="John Doe"
                  required={!isLogin}
                  minLength={2}
                />
                <p className="text-xs text-gray-500 mt-1">Your full name as you'd like it displayed</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Organization Name *
                </label>
                <input
                  type="text"
                  value={organizationName}
                  onChange={(e) => setOrganizationName(e.target.value)}
                  className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Acme Corporation"
                  required={!isLogin}
                  minLength={2}
                />
                <p className="text-xs text-gray-500 mt-1">Your company or organization name</p>
              </div>
            </>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Email Address *
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="you@company.com"
              required
            />
            {!isLogin && <p className="text-xs text-gray-500 mt-1">Use your work email address</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Password *
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => {
                setPassword(e.target.value);
                if (!isLogin) checkPasswordStrength(e.target.value);
              }}
              className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="••••••••"
              required
              minLength={8}
            />

            {!isLogin && password && (
              <div className="mt-2 space-y-1">
                <p className="text-xs font-medium text-gray-700">Password requirements:</p>
                <div className="text-xs space-y-1">
                  <div className={`flex items-center ${passwordStrength.hasMinLength ? 'text-green-600' : 'text-gray-500'}`}>
                    {passwordStrength.hasMinLength ? '✓' : '○'} At least 8 characters
                  </div>
                  <div className={`flex items-center ${passwordStrength.hasUppercase ? 'text-green-600' : 'text-gray-500'}`}>
                    {passwordStrength.hasUppercase ? '✓' : '○'} One uppercase letter
                  </div>
                  <div className={`flex items-center ${passwordStrength.hasLowercase ? 'text-green-600' : 'text-gray-500'}`}>
                    {passwordStrength.hasLowercase ? '✓' : '○'} One lowercase letter
                  </div>
                  <div className={`flex items-center ${passwordStrength.hasNumber ? 'text-green-600' : 'text-gray-500'}`}>
                    {passwordStrength.hasNumber ? '✓' : '○'} One number
                  </div>
                </div>
              </div>
            )}
          </div>

          <button
            type="submit"
            disabled={loading || (!isLogin && !isPasswordValid)}
            className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed font-medium"
          >
            {loading ? (
              <span className="flex items-center justify-center">
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                {isLogin ? 'Signing in...' : 'Creating account...'}
              </span>
            ) : (
              isLogin ? 'Sign In' : 'Create Account'
            )}
          </button>
        </form>

        <div className="mt-6 text-center">
          <button
            onClick={() => {
              setIsLogin(!isLogin);
              setError('');
              setPassword('');
              setPasswordStrength({
                hasMinLength: false,
                hasUppercase: false,
                hasLowercase: false,
                hasNumber: false
              });
            }}
            className="text-blue-600 hover:text-blue-800 text-sm font-medium"
          >
            {isLogin
              ? "Don't have an account? Sign Up →"
              : '← Already have an account? Sign In'}
          </button>
        </div>

        {isLogin && (
          <div className="mt-4 text-center">
            <a href="#" className="text-sm text-gray-500 hover:text-gray-700">
              Forgot your password?
            </a>
          </div>
        )}
      </div>
    </div>
  );
};
