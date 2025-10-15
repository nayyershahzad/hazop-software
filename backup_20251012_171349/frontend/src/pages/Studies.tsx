import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import type { Study } from '../types';
import { useAuthStore } from '../store/authStore';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const Studies = () => {
  const [studies, setStudies] = useState<Study[]>([]);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [facilityName, setFacilityName] = useState('');
  const [loading, setLoading] = useState(false);

  const { user, logout } = useAuthStore();
  const navigate = useNavigate();

  useEffect(() => {
    loadStudies();
  }, []);

  const loadStudies = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API_URL}/api/studies`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setStudies(response.data);
    } catch (err) {
      console.error('Failed to load studies:', err);
    }
  };

  const createStudy = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      await axios.post(
        `${API_URL}/api/studies`,
        { title, description, facility_name: facilityName },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setShowCreateModal(false);
      setTitle('');
      setDescription('');
      setFacilityName('');
      loadStudies();
    } catch (err) {
      console.error('Failed to create study:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <h1 className="text-2xl font-bold text-gray-900">HAZOP Studies</h1>
            <div className="flex items-center gap-4">
              <span className="text-sm text-gray-600">
                {user?.full_name} ({user?.role})
              </span>
              <button
                onClick={logout}
                className="text-sm text-red-600 hover:text-red-800"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-semibold text-gray-800">All Studies</h2>
          <button
            onClick={() => setShowCreateModal(true)}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            + New Study
          </button>
        </div>

        {/* Studies Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {studies.map((study) => (
            <div
              key={study.id}
              onClick={() => navigate(`/studies/${study.id}`)}
              className="bg-white p-6 rounded-lg shadow hover:shadow-lg transition-shadow cursor-pointer"
            >
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                {study.title}
              </h3>
              {study.facility_name && (
                <p className="text-sm text-gray-600 mb-2">
                  📍 {study.facility_name}
                </p>
              )}
              {study.description && (
                <p className="text-sm text-gray-500 mb-3 line-clamp-2">
                  {study.description}
                </p>
              )}
              <div className="flex justify-between items-center mt-4">
                <span className={`text-xs px-2 py-1 rounded ${
                  study.status === 'draft' ? 'bg-gray-100 text-gray-700' :
                  study.status === 'in_progress' ? 'bg-blue-100 text-blue-700' :
                  study.status === 'completed' ? 'bg-green-100 text-green-700' :
                  'bg-gray-100 text-gray-700'
                }`}>
                  {study.status.replace('_', ' ')}
                </span>
                <span className="text-xs text-gray-400">
                  {new Date(study.created_at).toLocaleDateString()}
                </span>
              </div>
            </div>
          ))}
        </div>

        {studies.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-500">No studies yet. Create your first one!</p>
          </div>
        )}
      </div>

      {/* Create Study Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h2 className="text-xl font-bold mb-4">Create New Study</h2>
            <form onSubmit={createStudy} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Study Title *
                </label>
                <input
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Facility Name
                </label>
                <input
                  type="text"
                  value={facilityName}
                  onChange={(e) => setFacilityName(e.target.value)}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Description
                </label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2"
                  rows={3}
                />
              </div>

              <div className="flex justify-end gap-2 mt-6">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400"
                >
                  {loading ? 'Creating...' : 'Create Study'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
