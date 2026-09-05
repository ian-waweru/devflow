import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { getTask } from '../api/tasks';
import { listComments, createComment, updateComment, deleteComment } from '../api/comments';
import { fetchAllPages } from '../utils/pagination';
import { getErrorMessage } from '../utils/errors';

const STATUS_LABELS = {
  todo: 'To Do',
  in_progress: 'In Progress',
  completed: 'Completed',
  archived: 'Archived',
};

const PRIORITY_STYLES = {
  low: 'bg-gray-700 text-gray-300',
  medium: 'bg-amber-500/20 text-amber-300',
  high: 'bg-red-500/20 text-red-300',
};

const TaskDetail = () => {
  const { taskId } = useParams();
  const { user } = useAuth();

  const [task, setTask] = useState(null);
  const [comments, setComments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [refreshKey, setRefreshKey] = useState(0);

  const [newComment, setNewComment] = useState('');
  const [commentError, setCommentError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const [editingId, setEditingId] = useState(null);
  const [editContent, setEditContent] = useState('');
  const [editSubmitting, setEditSubmitting] = useState(false);

  useEffect(() => {
    let ignore = false;

    const loadAll = async () => {
      try {
        const [taskRes, commentsRes] = await Promise.all([
          getTask(taskId),
          listComments({ task: taskId }),
        ]);
        if (ignore) return;

        const allComments = await fetchAllPages(commentsRes);
        if (ignore) return;

        setTask(taskRes.data);
        setComments(allComments);
        setError('');
      } catch (err) {
        if (ignore) return;
        setError(getErrorMessage(err, 'Could not load this task.'));
      } finally {
        if (!ignore) setLoading(false);
      }
    };

    loadAll();
    return () => {
      ignore = true;
    };
  }, [taskId, refreshKey]);

  const handleAddComment = async (e) => {
    e.preventDefault();
    setCommentError('');
    setSubmitting(true);
    try {
      await createComment({ task: taskId, content: newComment });
      setNewComment('');
      setRefreshKey((key) => key + 1);
    } catch (err) {
      setCommentError(getErrorMessage(err, 'Could not post comment.'));
    } finally {
      setSubmitting(false);
    }
  };

  const startEditing = (comment) => {
    setEditingId(comment.id);
    setEditContent(comment.content);
  };

  const cancelEditing = () => {
    setEditingId(null);
    setEditContent('');
  };

  const handleSaveEdit = async (commentId) => {
    setEditSubmitting(true);
    try {
      await updateComment(commentId, editContent);
      cancelEditing();
      setRefreshKey((key) => key + 1);
    } catch (err) {
      setCommentError(getErrorMessage(err, 'Could not update comment.'));
    } finally {
      setEditSubmitting(false);
    }
  };

  const handleDeleteComment = async (commentId) => {
    if (!window.confirm('Delete this comment?')) return;
    try {
      await deleteComment(commentId);
      setRefreshKey((key) => key + 1);
    } catch (err) {
      setCommentError(getErrorMessage(err, 'Could not delete comment.'));
    }
  };

  if (loading) return <p className="text-gray-400">Loading task...</p>;

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
      <Link to={`/projects/${task.project}`} className="text-indigo-400 hover:text-indigo-300 text-sm">
        ← Back to Project
      </Link>

      <div className="mt-3 mb-8">
        <div className="flex items-center gap-2 flex-wrap mb-2">
          <h1 className="text-2xl font-bold">{task.title}</h1>
          <span className={`text-xs px-2 py-0.5 rounded ${PRIORITY_STYLES[task.priority]}`}>
            {task.priority}
          </span>
          <span className="text-xs px-2 py-0.5 rounded bg-gray-700 text-gray-300">
            {STATUS_LABELS[task.status]}
          </span>
        </div>
        {task.description && <p className="text-gray-400">{task.description}</p>}
        <p className="text-xs text-gray-500 mt-2">
          {task.assigned_to_detail ? `Assigned to ${task.assigned_to_detail.username}` : 'Unassigned'}
          {' · '}Created by {task.created_by?.username}
        </p>
      </div>

      <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
        <h2 className="text-lg font-semibold mb-4">Comments</h2>

        {commentError && (
          <div className="mb-4 p-3 bg-red-500/10 border border-red-500 text-red-400 text-sm rounded">
            {commentError}
          </div>
        )}

        {comments.length === 0 ? (
          <p className="text-gray-400 text-sm mb-6">No comments yet.</p>
        ) : (
          <ul className="space-y-4 mb-6">
            {comments.map((comment) => {
              const isAuthor = comment.author.id === user.id;
              const isEditing = editingId === comment.id;
              return (
                <li key={comment.id} className="bg-gray-900/50 rounded p-4">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-medium">{comment.author.username}</span>
                    <span className="text-xs text-gray-500">
                      {new Date(comment.created_at).toLocaleString()}
                    </span>
                  </div>

                  {isEditing ? (
                    <div className="mt-2 space-y-2">
                      <textarea
                        rows={2}
                        value={editContent}
                        onChange={(e) => setEditContent(e.target.value)}
                        className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white text-sm focus:outline-none focus:border-indigo-500"
                      />
                      <div className="flex gap-3">
                        <button
                          onClick={() => handleSaveEdit(comment.id)}
                          disabled={editSubmitting}
                          className="text-xs text-indigo-400 hover:text-indigo-300 disabled:opacity-50"
                        >
                          Save
                        </button>
                        <button onClick={cancelEditing} className="text-xs text-gray-400 hover:text-gray-300">
                          Cancel
                        </button>
                      </div>
                    </div>
                  ) : (
                    <>
                      <p className="text-sm text-gray-300 whitespace-pre-wrap">{comment.content}</p>
                      {isAuthor && (
                        <div className="flex gap-3 mt-2">
                          <button
                            onClick={() => startEditing(comment)}
                            className="text-xs text-gray-400 hover:text-gray-300"
                          >
                            Edit
                          </button>
                          <button
                            onClick={() => handleDeleteComment(comment.id)}
                            className="text-xs text-red-400 hover:text-red-300"
                          >
                            Delete
                          </button>
                        </div>
                      )}
                    </>
                  )}
                </li>
              );
            })}
          </ul>
        )}

        <form onSubmit={handleAddComment} className="space-y-2">
          <textarea
            rows={3}
            required
            placeholder="Add a comment..."
            value={newComment}
            onChange={(e) => setNewComment(e.target.value)}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white text-sm focus:outline-none focus:border-indigo-500"
          />
          <button
            type="submit"
            disabled={submitting}
            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium rounded transition disabled:opacity-50"
          >
            {submitting ? 'Posting...' : 'Post Comment'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default TaskDetail;