import React, { useState, useEffect } from 'react';
import DashboardLayout from '../components/DashboardLayout';
import { userService } from '../services/services';
import { useAuth } from '../context/AuthContext';

const Profile = () => {
  const { user, setUser } = useAuth();
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    full_name: '',
    password: '',
    confirmPassword: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    if (user) {
      setFormData({
        email: user.email || '',
        username: user.username || '',
        full_name: user.full_name || '',
        password: '',
        confirmPassword: '',
      });
    }
  }, [user]);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    // Validation
    if (formData.password && formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (formData.password && formData.password.length < 6) {
      setError('Password must be at least 6 characters long');
      return;
    }

    setLoading(true);

    try {
      const updateData = {
        email: formData.email,
        username: formData.username,
        full_name: formData.full_name || null,
      };

      if (formData.password) {
        updateData.password = formData.password;
      }

      const updatedUser = await userService.updateProfile(updateData);
      setUser(updatedUser);
      setSuccess('Profile updated successfully!');
      setFormData((prev) => ({
        ...prev,
        password: '',
        confirmPassword: '',
      }));
    } catch (err) {
      console.error('Error updating profile:', err);
      setError(err.response?.data?.detail || 'Failed to update profile');
    } finally {
      setLoading(false);
    }
  };

  return (
    <DashboardLayout>
      <div className="max-w-2xl mx-auto space-y-6">
        <h1 className="text-3xl font-bold text-gray-900">Profile Settings</h1>

        {error && (
          <div className="bg-red-50 border border-red-400 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}

        {success && (
          <div className="bg-green-50 border border-green-400 text-green-700 px-4 py-3 rounded">
            {success}
          </div>
        )}

        {/* Profile Info Card */}
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">Account Information</h2>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <p className="text-gray-600">User ID</p>
              <p className="font-medium">{user?.id}</p>
            </div>
            <div>
              <p className="text-gray-600">Status</p>
              <span className={`badge ${user?.is_active ? 'badge-success' : 'badge-danger'}`}>
                {user?.is_active ? 'Active' : 'Inactive'}
              </span>
            </div>
            <div>
              <p className="text-gray-600">Member Since</p>
              <p className="font-medium">
                {user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A'}
              </p>
            </div>
            <div>
              <p className="text-gray-600">Verified</p>
              <span className={`badge ${user?.is_verified ? 'badge-success' : 'badge-warning'}`}>
                {user?.is_verified ? 'Verified' : 'Not Verified'}
              </span>
            </div>
          </div>
        </div>

        {/* Update Profile Form */}
        <form onSubmit={handleSubmit} className="card space-y-4">
          <h2 className="text-xl font-semibold">Update Profile</h2>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              className="input-field"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Username</label>
            <input
              type="text"
              name="username"
              value={formData.username}
              onChange={handleChange}
              className="input-field"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Full Name
            </label>
            <input
              type="text"
              name="full_name"
              value={formData.full_name}
              onChange={handleChange}
              className="input-field"
            />
          </div>

          <hr className="my-4" />

          <h3 className="text-lg font-semibold">Change Password</h3>
          <p className="text-sm text-gray-600">Leave blank to keep current password</p>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              New Password
            </label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              className="input-field"
              placeholder="••••••••"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Confirm New Password
            </label>
            <input
              type="password"
              name="confirmPassword"
              value={formData.confirmPassword}
              onChange={handleChange}
              className="input-field"
              placeholder="••••••••"
            />
          </div>

          <div className="flex gap-4 pt-4">
            <button type="submit" disabled={loading} className="btn-primary">
              {loading ? 'Updating...' : 'Update Profile'}
            </button>
            <button
              type="button"
              onClick={() => {
                setFormData({
                  email: user?.email || '',
                  username: user?.username || '',
                  full_name: user?.full_name || '',
                  password: '',
                  confirmPassword: '',
                });
                setError('');
                setSuccess('');
              }}
              className="btn-secondary"
            >
              Reset
            </button>
          </div>
        </form>

        {/* Danger Zone */}
        <div className="card border-red-300 bg-red-50">
          <h3 className="text-lg font-semibold text-red-900 mb-2">Danger Zone</h3>
          <p className="text-sm text-red-700 mb-4">
            Once you delete your account, there is no going back. Please be certain.
          </p>
          <button
            onClick={async () => {
              if (
                window.confirm(
                  'Are you sure you want to delete your account? This action cannot be undone.'
                )
              ) {
                try {
                  await userService.deleteProfile();
                  window.location.href = '/login';
                } catch (err) {
                  setError('Failed to delete account');
                }
              }
            }}
            className="btn-danger"
          >
            Delete Account
          </button>
        </div>
      </div>
    </DashboardLayout>
  );
};

export default Profile;
