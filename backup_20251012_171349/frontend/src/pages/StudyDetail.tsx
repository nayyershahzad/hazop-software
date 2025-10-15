import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import type { Study, Node, Deviation } from '../types';
import { HAZOPAnalysis } from '../components/HAZOPAnalysis';
import { PIDViewer } from '../components/PIDViewer';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const StudyDetail = () => {
  const { studyId } = useParams();
  const navigate = useNavigate();
  const [study, setStudy] = useState<Study | null>(null);
  const [nodes, setNodes] = useState<Node[]>([]);
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);
  const [deviations, setDeviations] = useState<Deviation[]>([]);
  const [selectedDeviation, setSelectedDeviation] = useState<Deviation | null>(null);
  const [showNodeModal, setShowNodeModal] = useState(false);
  const [showDeviationModal, setShowDeviationModal] = useState(false);
  const [showDuplicateModal, setShowDuplicateModal] = useState(false);
  const [nodeToDuplicate, setNodeToDuplicate] = useState<Node | null>(null);
  const [editingNode, setEditingNode] = useState<Node | null>(null);

  const [nodeForm, setNodeForm] = useState({
    node_number: '',
    node_name: '',
    description: '',
    design_intent: ''
  });

  const [deviationForm, setDeviationForm] = useState({
    parameter: 'Flow',
    guide_word: 'No',
    deviation_description: ''
  });

  const [duplicateForm, setDuplicateForm] = useState({
    new_node_number: '',
    new_node_name: '',
    include_deviations: true,
    include_causes: true,
    include_consequences: true,
    include_safeguards: true,
    include_recommendations: true
  });

  const parameters = ['Flow', 'Pressure', 'Temperature', 'Level', 'Composition', 'Phase'];
  const guideWords = ['No', 'More', 'Less', 'Reverse', 'Part of', 'As well as', 'Other than'];

  useEffect(() => {
    loadStudy();
    loadNodes();
  }, [studyId]);

  useEffect(() => {
    if (selectedNode) {
      loadDeviations(selectedNode.id);
    }
  }, [selectedNode]);

  const loadStudy = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API_URL}/api/studies/${studyId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setStudy(response.data);
    } catch (err) {
      console.error('Failed to load study:', err);
    }
  };

  const loadNodes = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API_URL}/api/studies/${studyId}/nodes`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setNodes(response.data);
    } catch (err) {
      console.error('Failed to load nodes:', err);
    }
  };

  const loadDeviations = async (nodeId: string) => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API_URL}/api/studies/nodes/${nodeId}/deviations`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setDeviations(response.data);
    } catch (err) {
      console.error('Failed to load deviations:', err);
    }
  };

  const openNodeModal = () => {
    setEditingNode(null);
    setNodeForm({ node_number: '', node_name: '', description: '', design_intent: '' });
    setShowNodeModal(true);
  };

  const openEditNodeModal = (node: Node, e: React.MouseEvent) => {
    e.stopPropagation();
    setEditingNode(node);
    setNodeForm({
      node_number: node.node_number,
      node_name: node.node_name,
      description: node.description || '',
      design_intent: node.design_intent || ''
    });
    setShowNodeModal(true);
  };

  const createOrUpdateNode = async (e: React.FormEvent) => {
    e.preventDefault();

    if (editingNode) {
      // Update existing node
      try {
        const token = localStorage.getItem('token');
        await axios.put(`${API_URL}/api/studies/nodes/${editingNode.id}`, nodeForm, {
          headers: { Authorization: `Bearer ${token}` }
        });
        setShowNodeModal(false);
        setEditingNode(null);
        setNodeForm({ node_number: '', node_name: '', description: '', design_intent: '' });
        loadNodes();
      } catch (err) {
        console.error('Failed to update node:', err);
        alert('Failed to update node');
      }
    } else {
      // Create new node
      try {
        const token = localStorage.getItem('token');
        await axios.post(
          `${API_URL}/api/studies/${studyId}/nodes`,
          nodeForm,
          { headers: { Authorization: `Bearer ${token}` } }
        );
        setShowNodeModal(false);
        setNodeForm({ node_number: '', node_name: '', description: '', design_intent: '' });
        loadNodes();
      } catch (err) {
        console.error('Failed to create node:', err);
        alert('Failed to create node');
      }
    }
  };

  const openDeviationModal = () => {
    setDeviationForm({ parameter: 'Flow', guide_word: 'No', deviation_description: '' });
    setShowDeviationModal(true);
  };

  const deleteStudy = async () => {
    if (!confirm('⚠️ WARNING: Delete this entire study?\n\nThis will permanently delete:\n• All nodes\n• All deviations\n• All causes, consequences, safeguards\n• All P&ID documents and markers\n• All risk assessments\n\nThis action cannot be undone!')) return;

    try {
      const token = localStorage.getItem('token');
      await axios.delete(`${API_URL}/api/studies/${studyId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      alert('Study deleted successfully');
      navigate('/studies'); // Redirect to studies list
    } catch (err) {
      console.error('Failed to delete study:', err);
      alert('Failed to delete study');
    }
  };

  const deleteNode = async (nodeId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm('Delete this node and all its deviations?')) return;

    try {
      const token = localStorage.getItem('token');
      await axios.delete(`${API_URL}/api/studies/nodes/${nodeId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (selectedNode?.id === nodeId) {
        setSelectedNode(null);
        setDeviations([]);
      }
      loadNodes();
    } catch (err) {
      console.error('Failed to delete node:', err);
    }
  };

  const deleteDeviation = async (deviationId: string) => {
    if (!confirm('Delete this deviation and all its analysis data?')) return;

    try {
      const token = localStorage.getItem('token');
      await axios.delete(`${API_URL}/api/studies/deviations/${deviationId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (selectedDeviation?.id === deviationId) {
        setSelectedDeviation(null);
      }
      if (selectedNode) {
        loadDeviations(selectedNode.id);
      }
    } catch (err) {
      console.error('Failed to delete deviation:', err);
    }
  };

  const openDuplicateModal = (node: Node) => {
    setNodeToDuplicate(node);
    setDuplicateForm({
      new_node_number: '',
      new_node_name: '',
      include_deviations: true,
      include_causes: true,
      include_consequences: true,
      include_safeguards: true,
      include_recommendations: true
    });
    setShowDuplicateModal(true);
  };

  const duplicateNode = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!nodeToDuplicate) return;

    try {
      const token = localStorage.getItem('token');
      await axios.post(
        `${API_URL}/api/studies/nodes/${nodeToDuplicate.id}/duplicate`,
        duplicateForm,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setShowDuplicateModal(false);
      setNodeToDuplicate(null);
      loadNodes();
    } catch (err) {
      console.error('Failed to duplicate node:', err);
      alert('Failed to duplicate node');
    }
  };

  const createDeviation = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedNode) return;

    try {
      const token = localStorage.getItem('token');
      await axios.post(
        `${API_URL}/api/studies/nodes/${selectedNode.id}/deviations`,
        deviationForm,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setShowDeviationModal(false);
      setDeviationForm({ parameter: 'Flow', guide_word: 'No', deviation_description: '' });
      loadDeviations(selectedNode.id);
    } catch (err) {
      console.error('Failed to create deviation:', err);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="w-full mx-0 px-2 py-4">
          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">{study?.title}</h1>
              {study?.facility_name && (
                <p className="text-sm text-gray-600 mt-1">📍 {study.facility_name}</p>
              )}
            </div>
            <button
              onClick={deleteStudy}
              className="flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
              title="Delete entire study"
            >
              <span>🗑️</span>
              <span>Delete Study</span>
            </button>
          </div>
        </div>
      </div>

      <div className="w-full mx-0 px-2 py-8 pb-20">
        <div className="grid grid-cols-1 lg:grid-cols-6 gap-6">
          {/* Nodes List - Reduced width */}
          <div className="lg:col-span-1 bg-white rounded-lg shadow p-4">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-semibold">Nodes</h2>
              <button
                onClick={openNodeModal}
                className="bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700"
              >
                + Add Node
              </button>
            </div>

            <div className="space-y-2">
              {nodes.map((node) => (
                <div
                  key={node.id}
                  onClick={() => setSelectedNode(node)}
                  className={`p-3 rounded cursor-pointer transition-colors ${
                    selectedNode?.id === node.id
                      ? 'bg-blue-100 border border-blue-300'
                      : 'bg-gray-50 hover:bg-gray-100'
                  }`}
                >
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="font-medium text-sm">{node.node_number}</div>
                      <div className="text-xs text-gray-600">{node.node_name}</div>
                    </div>
                    <div className="flex gap-1">
                      <button
                        onClick={(e) => openEditNodeModal(node, e)}
                        className="text-green-600 hover:text-green-800 text-xs"
                        title="Edit node"
                      >
                        ✏️
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          openDuplicateModal(node);
                        }}
                        className="text-blue-600 hover:text-blue-800 text-xs"
                        title="Duplicate node"
                      >
                        📋
                      </button>
                      <button
                        onClick={(e) => deleteNode(node.id, e)}
                        className="text-red-600 hover:text-red-800 text-xs"
                        title="Delete node"
                      >
                        🗑️
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {nodes.length === 0 && (
              <p className="text-sm text-gray-500 text-center py-8">No nodes yet</p>
            )}
          </div>

          {/* Deviations - Increased width */}
          <div className="lg:col-span-5 space-y-4">
            <div className="bg-white rounded-lg shadow p-4">
              {selectedNode ? (
                <>
                  <div className="flex justify-between items-center mb-4">
                    <div>
                      <h2 className="text-lg font-semibold">
                        {selectedNode.node_number} - {selectedNode.node_name}
                      </h2>
                      {selectedNode.design_intent && (
                        <p className="text-sm text-gray-600 mt-1">
                          Design Intent: {selectedNode.design_intent}
                        </p>
                      )}
                    </div>
                    <button
                      onClick={openDeviationModal}
                      className="bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700"
                    >
                      + Add Deviation
                    </button>
                  </div>

                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                            Parameter
                          </th>
                          <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                            Guide Word
                          </th>
                          <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                            Deviation
                          </th>
                          <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                            Actions
                          </th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {deviations.map((dev) => (
                          <tr key={dev.id} className={selectedDeviation?.id === dev.id ? 'bg-blue-50' : ''}>
                            <td className="px-3 py-2 text-sm">{dev.parameter}</td>
                            <td className="px-3 py-2 text-sm">{dev.guide_word}</td>
                            <td className="px-3 py-2 text-sm">{dev.deviation_description}</td>
                            <td className="px-3 py-2 text-sm">
                              <div className="flex gap-2">
                                <button
                                  onClick={() => setSelectedDeviation(dev)}
                                  className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                                >
                                  {selectedDeviation?.id === dev.id ? '✓ Analyzing' : 'Analyze'}
                                </button>
                                <button
                                  onClick={() => deleteDeviation(dev.id)}
                                  className="text-red-600 hover:text-red-800 text-sm"
                                  title="Delete deviation"
                                >
                                  🗑️
                                </button>
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>

                    {deviations.length === 0 && (
                      <p className="text-sm text-gray-500 text-center py-8">
                        No deviations yet. Add one to begin HAZOP analysis.
                      </p>
                    )}
                  </div>
                </>
              ) : (
                <div className="text-center py-12">
                  <p className="text-gray-500">Select a node to view deviations</p>
                </div>
              )}
            </div>

            {/* HAZOP Analysis Section */}
            {selectedDeviation && (
              <HAZOPAnalysis deviation={selectedDeviation} />
            )}
          </div>
        </div>
      </div>

      {/* Node Modal */}
      {showNodeModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h2 className="text-xl font-bold mb-4">{editingNode ? 'Edit Node' : 'Add New Node'}</h2>
            <form onSubmit={createOrUpdateNode} className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">Node Number *</label>
                <input
                  type="text"
                  value={nodeForm.node_number}
                  onChange={(e) => setNodeForm({ ...nodeForm, node_number: e.target.value })}
                  className="w-full border rounded px-3 py-2"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Node Name *</label>
                <input
                  type="text"
                  value={nodeForm.node_name}
                  onChange={(e) => setNodeForm({ ...nodeForm, node_name: e.target.value })}
                  className="w-full border rounded px-3 py-2"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Description</label>
                <textarea
                  value={nodeForm.description}
                  onChange={(e) => setNodeForm({ ...nodeForm, description: e.target.value })}
                  className="w-full border rounded px-3 py-2"
                  rows={2}
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Design Intent</label>
                <textarea
                  value={nodeForm.design_intent}
                  onChange={(e) => setNodeForm({ ...nodeForm, design_intent: e.target.value })}
                  className="w-full border rounded px-3 py-2"
                  rows={2}
                />
              </div>
              <div className="flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setShowNodeModal(false)}
                  className="px-4 py-2 border rounded hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
                  {editingNode ? 'Update Node' : 'Create Node'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Deviation Modal */}
      {showDeviationModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h2 className="text-xl font-bold mb-4">Add Deviation</h2>
            <form onSubmit={createDeviation} className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">Parameter *</label>
                <select
                  value={deviationForm.parameter}
                  onChange={(e) => setDeviationForm({ ...deviationForm, parameter: e.target.value })}
                  className="w-full border rounded px-3 py-2"
                >
                  {parameters.map((p) => (
                    <option key={p} value={p}>{p}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Guide Word *</label>
                <select
                  value={deviationForm.guide_word}
                  onChange={(e) => setDeviationForm({ ...deviationForm, guide_word: e.target.value })}
                  className="w-full border rounded px-3 py-2"
                >
                  {guideWords.map((g) => (
                    <option key={g} value={g}>{g}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Deviation Description *</label>
                <textarea
                  value={deviationForm.deviation_description}
                  onChange={(e) => setDeviationForm({ ...deviationForm, deviation_description: e.target.value })}
                  className="w-full border rounded px-3 py-2"
                  rows={3}
                  required
                />
              </div>
              <div className="flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setShowDeviationModal(false)}
                  className="px-4 py-2 border rounded hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button type="submit" className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700">
                  Create Deviation
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Duplicate Node Modal */}
      {showDuplicateModal && nodeToDuplicate && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h2 className="text-xl font-bold mb-4">
              Duplicate Node: {nodeToDuplicate.node_number}
            </h2>
            <form onSubmit={duplicateNode} className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">New Node Number *</label>
                <input
                  type="text"
                  value={duplicateForm.new_node_number}
                  onChange={(e) => setDuplicateForm({ ...duplicateForm, new_node_number: e.target.value })}
                  className="w-full border rounded px-3 py-2"
                  placeholder="e.g., N-002"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">New Node Name *</label>
                <input
                  type="text"
                  value={duplicateForm.new_node_name}
                  onChange={(e) => setDuplicateForm({ ...duplicateForm, new_node_name: e.target.value })}
                  className="w-full border rounded px-3 py-2"
                  placeholder="e.g., Reactor Inlet"
                  required
                />
              </div>

              <div className="border-t pt-3 mt-3">
                <p className="text-sm font-medium mb-2">Include:</p>
                <div className="space-y-2">
                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={duplicateForm.include_deviations}
                      onChange={(e) => setDuplicateForm({ ...duplicateForm, include_deviations: e.target.checked })}
                    />
                    <span className="text-sm">Deviations</span>
                  </label>
                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={duplicateForm.include_causes}
                      onChange={(e) => setDuplicateForm({ ...duplicateForm, include_causes: e.target.checked })}
                    />
                    <span className="text-sm">Causes</span>
                  </label>
                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={duplicateForm.include_consequences}
                      onChange={(e) => setDuplicateForm({ ...duplicateForm, include_consequences: e.target.checked })}
                    />
                    <span className="text-sm">Consequences</span>
                  </label>
                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={duplicateForm.include_safeguards}
                      onChange={(e) => setDuplicateForm({ ...duplicateForm, include_safeguards: e.target.checked })}
                    />
                    <span className="text-sm">Safeguards</span>
                  </label>
                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={duplicateForm.include_recommendations}
                      onChange={(e) => setDuplicateForm({ ...duplicateForm, include_recommendations: e.target.checked })}
                    />
                    <span className="text-sm">Recommendations</span>
                  </label>
                </div>
              </div>

              <div className="flex justify-end gap-2 mt-4">
                <button
                  type="button"
                  onClick={() => {
                    setShowDuplicateModal(false);
                    setNodeToDuplicate(null);
                  }}
                  className="px-4 py-2 border rounded hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                >
                  📋 Duplicate Node
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* P&ID Viewer - Fixed Bottom Panel */}
      {studyId && (
        <PIDViewer
          studyId={studyId}
          selectedNodeId={selectedNode?.id}
          onNodeMarked={loadNodes}
        />
      )}
    </div>
  );
};
