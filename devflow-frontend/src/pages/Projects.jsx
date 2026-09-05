import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { listProjects, createProject } from '../api/projects';
import { fetchAllPages } from '../utils/pagination';
import { getErrorMessage } from '../utils/errors';

const Projects = () => {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [refreshKey, setRefreshKey] = useState(0);

  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ name: '', description: '' });
  const [formError, setFormError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    let ignore = false;

    const loadProjects = async () => {
      try {
        const response = await listProjects();
        const allProjects = await fetchAllPages(response);
        if (ignore) return;
        setProjects(allProjects);
        setError('');
      } catch (err) {
        if (ignore) return;
        setError(getErrorMessage(err, 'Could not load projects.'));
      } finally {
        if (!ignore) setLoading(false);
      }
    };

    loadProjects();
    return () => {
      ignore = true;
    };
  }, [refreshKey]);

  const handleCreate = async (e) => {
    e.preventDefault();
    setFormError('');
    setSubmitting(true);

    try {
      await createProject(form);
      setForm({ name: '', description: '' });
      setShowForm(false);
      setRefreshKey((key) => key + 1);
    } catch (err) {
      setFormError(getErrorMessage(err, 'Could not create project.'));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold">Projects</h1>
          <p className="text-gray-400 mt-1">Everything you own or belong to.</p>
        </div>
        <button
          onClick={() => setShowForm((prev) => !prev)}
          className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium rounded transition"
        >
          {showForm ? 'Cancel' : 'New Project'}
        </button>
      </div>

      {showForm && (
        <form
          onSubmit={handleCreate}
          className="mb-8 bg-gray-800 border border-gray-700 rounded-lg p-6 space-y-4"
        >
          {formError && (
            <div className="p-3 bg-red-500/10 border border-red-500 text-red-400 text-sm rounded">
              {formError}
            </div>
          )}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">Name</label>
            <input
              type="text"
              required
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded text-white focus:outline-none focus:border-indigo-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">
              Description <span className="text-gray-500">(optional)</span>
            </label>
            <textarea
              rows={3}
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
              className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded text-white focus:outline-none focus:border-indigo-500"
            />
          </div>
          <button
            type="submit"
            disabled={submitting}
            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-semibold rounded transition disabled:opacity-50"
          >
            {submitting ? 'Creating...' : 'Create Project'}
          </button>
        </form>
      )}

      {loading && <p className="text-gray-400">Loading projects...</p>}

      {!loading && error && (
        <div className="p-3 bg-red-500/10 border border-red-500 text-red-400 text-sm rounded">
          {error}
        </div>
      )}

      {!loading && !error && projects.length === 0 && (
        <div className="bg-gray-800 border border-gray-700 rounded-lg p-8 text-center text-gray-400">
          No projects yet. Create one to get started.
        </div>
      )}

      {!loading && !error && projects.length > 0 && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {projects.map((project) => (
            <Link
              key={project.id}
              to={`/projects/${project.id}`}
              className="block bg-gray-800 border border-gray-700 rounded-lg p-5 hover:border-indigo-500 transition"
            >
              <h2 className="font-semibold text-lg mb-1 truncate">{project.name}</h2>
              <p className="text-gray-400 text-sm mb-4 line-clamp-2">
                {project.description || 'No description.'}
              </p>
              <div className="flex items-center justify-between text-xs text-gray-500">
                <span>Owner: {project.owner?.username}</span>
                <span>
                  {project.members_count} member{project.members_count === 1 ? '' : 's'}
                </span>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
};

export default Projects;