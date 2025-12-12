import React, { useEffect, useState } from 'react';
import DashboardLayout from '../components/DashboardLayout';
import { noteService } from '../services/services';

const Notes = () => {
  const [notes, setNotes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editingNote, setEditingNote] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [formData, setFormData] = useState({
    title: '',
    content: '',
    tags: '',
    is_pinned: false,
  });

  useEffect(() => {
    fetchNotes();
  }, [searchTerm]);

  const fetchNotes = async () => {
    try {
      setLoading(true);
      const params = searchTerm ? { search: searchTerm } : {};
      const data = await noteService.getNotes(params);
      setNotes(data);
    } catch (err) {
      console.error('Error fetching notes:', err);
      setError('Failed to load notes');
    } finally {
      setLoading(false);
    }
  };

  const handleOpenModal = (note = null) => {
    if (note) {
      setEditingNote(note);
      setFormData({
        title: note.title,
        content: note.content || '',
        tags: note.tags || '',
        is_pinned: note.is_pinned,
      });
    } else {
      setEditingNote(null);
      setFormData({
        title: '',
        content: '',
        tags: '',
        is_pinned: false,
      });
    }
    setShowModal(true);
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setEditingNote(null);
    setFormData({
      title: '',
      content: '',
      tags: '',
      is_pinned: false,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    try {
      if (editingNote) {
        await noteService.updateNote(editingNote.id, formData);
      } else {
        await noteService.createNote(formData);
      }
      await fetchNotes();
      handleCloseModal();
    } catch (err) {
      console.error('Error saving note:', err);
      setError(err.response?.data?.detail || 'Failed to save note');
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this note?')) {
      return;
    }

    try {
      await noteService.deleteNote(id);
      await fetchNotes();
    } catch (err) {
      console.error('Error deleting note:', err);
      setError('Failed to delete note');
    }
  };

  const handleTogglePin = async (note) => {
    try {
      await noteService.updateNote(note.id, { is_pinned: !note.is_pinned });
      await fetchNotes();
    } catch (err) {
      console.error('Error toggling pin:', err);
      setError('Failed to update note');
    }
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold text-gray-900">Notes</h1>
          <button onClick={() => handleOpenModal()} className="btn-primary">
            ➕ New Note
          </button>
        </div>

        {/* Search */}
        <div className="card">
          <input
            type="text"
            className="input-field"
            placeholder="Search notes..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        {error && (
          <div className="bg-red-50 border border-red-400 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}

        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
          </div>
        ) : notes.length === 0 ? (
          <div className="card text-center py-12">
            <p className="text-gray-500 text-lg">No notes found</p>
            <p className="text-gray-400 text-sm mt-2">
              {searchTerm ? 'Try a different search term' : 'Create your first note to get started'}
            </p>
            <button onClick={() => handleOpenModal()} className="btn-primary mt-4">
              Create Note
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {notes.map((note) => (
              <div
                key={note.id}
                className={`card hover:shadow-lg transition-shadow ${
                  note.is_pinned ? 'ring-2 ring-primary-500' : ''
                }`}
              >
                <div className="flex items-start justify-between mb-3">
                  <h3 className="text-lg font-semibold text-gray-900 flex-1">
                    {note.title}
                    {note.is_pinned && <span className="ml-2">📌</span>}
                  </h3>
                  <button
                    onClick={() => handleTogglePin(note)}
                    className="text-gray-400 hover:text-primary-600"
                  >
                    {note.is_pinned ? '📍' : '📌'}
                  </button>
                </div>

                {note.content && (
                  <p className="text-gray-600 text-sm mb-3 line-clamp-3">{note.content}</p>
                )}

                {note.tags && (
                  <div className="flex flex-wrap gap-2 mb-3">
                    {note.tags.split(',').map((tag, idx) => (
                      <span key={idx} className="badge badge-info">
                        {tag.trim()}
                      </span>
                    ))}
                  </div>
                )}

                <div className="text-xs text-gray-500 mb-3">
                  {new Date(note.updated_at || note.created_at).toLocaleString()}
                </div>

                <div className="flex gap-2">
                  <button
                    onClick={() => handleOpenModal(note)}
                    className="flex-1 btn-secondary text-sm"
                  >
                    ✏️ Edit
                  </button>
                  <button
                    onClick={() => handleDelete(note.id)}
                    className="flex-1 btn-danger text-sm"
                  >
                    🗑️ Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Modal */}
        {showModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-8 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
              <h2 className="text-2xl font-bold mb-4">
                {editingNote ? 'Edit Note' : 'New Note'}
              </h2>

              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Title
                  </label>
                  <input
                    type="text"
                    className="input-field"
                    value={formData.title}
                    onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                    placeholder="Note title"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Content
                  </label>
                  <textarea
                    className="input-field"
                    rows="6"
                    value={formData.content}
                    onChange={(e) => setFormData({ ...formData, content: e.target.value })}
                    placeholder="Write your note here..."
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Tags (comma-separated)
                  </label>
                  <input
                    type="text"
                    className="input-field"
                    value={formData.tags}
                    onChange={(e) => setFormData({ ...formData, tags: e.target.value })}
                    placeholder="trading, strategy, important"
                  />
                </div>

                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id="is_pinned"
                    checked={formData.is_pinned}
                    onChange={(e) =>
                      setFormData({ ...formData, is_pinned: e.target.checked })
                    }
                    className="rounded"
                  />
                  <label htmlFor="is_pinned" className="text-sm text-gray-700">
                    Pin this note
                  </label>
                </div>

                <div className="flex gap-3 mt-6">
                  <button type="submit" className="flex-1 btn-primary">
                    {editingNote ? 'Update' : 'Create'}
                  </button>
                  <button
                    type="button"
                    onClick={handleCloseModal}
                    className="flex-1 btn-secondary"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
};

export default Notes;
