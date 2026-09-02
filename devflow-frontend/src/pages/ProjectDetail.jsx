import { useEffect, useState } from 'react';
import { useNavigate, useParams, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  getProject,
  getProjectMembers,
  getProjectActivity,
  addProjectMember,
  removeProjectMember,
  deleteProject,
} from '../api/projects';
import { getErrorMessage } from '../utils/errors';

const ProjectDetail = () => {
  const { id } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();

  const [project, setProject] = useState(null);
  const [members, setMembers] = useState([]);
  const [activity, setActivity] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [refreshKey, setRefreshKey] = useState(0);

  const [newUsername, setNewUsername] = useState('');
  const [memberError, setMemberError] = useState('');
  const [memberActionPending, setMemberActionPending] = useState(false);

  const isOwner = project && user && project.owner?.id === user.id;

  useEffect(() => {
    let ignore = false;

    const loadAll = async () => {
      try {
        const [projectRes, membersRes, activityRes] = await Promise.all([
          getProject(id),
          getProjectMembers(id),
          getProjectActivity(id),
        ]);
        if (ignore) return;
        setProject(projectRes.data);
        setMembers(membersRes.data.results);
        setActivity(activityRes.data.results);
        setError('');
      } catch (err) {
        if (ignore) return;
        setError(getErrorMessage(err, 'Could not load this project.'));
      } finally {
        if (!ignore) setLoading(false);
      }
    };

    loadAll();
    return () => {
      ignore = true;
    };
  }, [id, refreshKey]);

  const handleAddMember = async (e) => {
    e.preventDefault();
    setMemberError('');
    setMemberActionPending(true);
    try {
      await addProjectMember(id, newUsername.trim());
      setNewUsername('');
      setRefreshKey((key) => key + 1);
    } catch (err) {
      setMemberError(getErrorMessage(err, 'Could not add that member.'));
    } finally {
      setMemberActionPending(false);
    }
  };

  const handleRemoveMember = async (username) => {
    setMemberError('');
    setMemberActionPending(true);
    try {
      await removeProjectMember(id, username);
      setRefreshKey((key) => key + 1);
    } catch (err) {
      setMemberError(getErrorMessage(err, 'Could not remove that member.'));
    } finally {
      setMemberActionPending(false);
    }
  };

  const handleDeleteProject = async () => {
    if (!window.confirm(`Delete "${project.name}"? This cannot be undone.`)) return;
    try {
      await deleteProject(id);
      navigate('/projects');
    } catch (err) {
      setError(getErrorMessage(err, 'Could not delete this project.'));
    }
  };

  if (loading) return <p className="text-gray-400">Loading project...</p>;

  if (error) {
    return (
      <div>
        <div className="p-3 bg-red-500/10 border border-red-500 text-red-400 text-sm rounded mb-4">
          {error}
        </div>
        <Link to="/projects" className="text-indigo-400 hover:text-indigo-300 text-sm">
          ← Back to Projects
        </Link>
      </div>
    );
  }

  return (
    <div>
      <Link to="/projects" className="text-indigo-400 hover:text-indigo-300 text-sm">
        ← Back to Projects
      </Link>

      <div className="flex items-start justify-between mt-3 mb-8">
        <div>
          <h1 className="text-2xl font-bold">{project.name}</h1>
          <p className="text-gray-400 mt-1">{project.description || 'No description.'}</p>
          <p className="text-xs text-gray-500 mt-2">Owned by {project.owner?.username}</p>
        </div>
        {isOwner && (
          <button
            onClick={handleDeleteProject}
            className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white text-sm font-medium rounded transition"
          >
            Delete Project
          </button>
        )}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Members */}
        <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
          <h2 className="text-lg font-semibold mb-4">Members</h2>

          {memberError && (
            <div className="mb-4 p-3 bg-red-500/10 border border-red-500 text-red-400 text-sm rounded">
              {memberError}
            </div>
          )}

          <ul className="space-y-2 mb-4">
            {members.map((membership) => (
              <li
                key={membership.id}
                className="flex items-center justify-between bg-gray-900/50 px-3 py-2 rounded"
              >
                <div className="flex items-center gap-2">
                  <span className="text-sm">{membership.user.username}</span>
                  <span
                    className={`text-xs px-2 py-0.5 rounded ${
                      membership.role === 'owner'
                        ? 'bg-indigo-500/20 text-indigo-300'
                        : 'bg-gray-700 text-gray-400'
                    }`}
                  >
                    {membership.role}
                  </span>
                </div>
                {isOwner && membership.role !== 'owner' && (
                  <button
                    onClick={() => handleRemoveMember(membership.user.username)}
                    disabled={memberActionPending}
                    className="text-xs text-red-400 hover:text-red-300 disabled:opacity-50"
                  >
                    Remove
                  </button>
                )}
              </li>
            ))}
          </ul>

          {isOwner && (
            <form onSubmit={handleAddMember} className="flex gap-2">
              <input
                type="text"
                placeholder="Username to add"
                required
                value={newUsername}
                onChange={(e) => setNewUsername(e.target.value)}
                className="flex-1 px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white text-sm focus:outline-none focus:border-indigo-500"
              />
              <button
                type="submit"
                disabled={memberActionPending}
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium rounded transition disabled:opacity-50"
              >
                Add
              </button>
            </form>
          )}
        </div>

        {/* Activity */}
        <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
          <h2 className="text-lg font-semibold mb-4">Activity</h2>
          {activity.length === 0 ? (
            <p className="text-gray-400 text-sm">No activity yet.</p>
          ) : (
            <ul className="space-y-3">
              {activity.map((entry) => (
                <li key={entry.id} className="text-sm">
                  <span className="text-gray-300">{entry.action}</span>
                  <div className="text-xs text-gray-500 mt-0.5">
                    {new Date(entry.timestamp).toLocaleString()}
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProjectDetail;