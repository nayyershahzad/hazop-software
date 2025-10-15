import { useState, useEffect, useRef, useMemo } from 'react';
import { Document, Page, pdfjs } from 'react-pdf';
import axios from 'axios';
// Import PDF styles separately to avoid conflicts with Tailwind
import '../pdf-styles.css';

// Configure PDF.js worker - use local worker file served from public folder
pdfjs.GlobalWorkerOptions.workerSrc = '/pdf.worker.min.mjs';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface PIDViewerProps {
  studyId: string;
  selectedNodeId?: string;
  onNodeMarked?: () => void;
}

interface PIDDocument {
  id: string;
  study_id: string;
  filename: string;
  total_pages: number;
  uploaded_at: string;
}

interface NodeLocation {
  id: string;
  node_id: string;
  pid_document_id: string;
  page_number: number;
  x_coordinate: number;
  y_coordinate: number;
  width: number;
  height: number;
  color: string;
}

export const PIDViewer = ({ studyId, selectedNodeId, onNodeMarked }: PIDViewerProps) => {
  const [pidDocuments, setPidDocuments] = useState<PIDDocument[]>([]);
  const [selectedPID, setSelectedPID] = useState<PIDDocument | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [numPages, setNumPages] = useState(0);
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);
  const [nodeLocations, setNodeLocations] = useState<NodeLocation[]>([]);
  const [markingMode, setMarkingMode] = useState(false);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [isExpanded, setIsExpanded] = useState(false);
  const [selectedColor, setSelectedColor] = useState('#FFFF00'); // Default yellow
  const [isDrawing, setIsDrawing] = useState(false);
  const [drawStart, setDrawStart] = useState<{ x: number; y: number } | null>(null);
  const [currentDraw, setCurrentDraw] = useState<{ x: number; y: number; width: number; height: number } | null>(null);
  const [hoveredHighlight, setHoveredHighlight] = useState<string | null>(null);
  const [draggedHighlight, setDraggedHighlight] = useState<string | null>(null);
  const [dragOffset, setDragOffset] = useState<{ x: number; y: number } | null>(null);
  const [resizingHighlight, setResizingHighlight] = useState<{ id: string; corner: string } | null>(null);
  const [undoStack, setUndoStack] = useState<Array<{ action: string; locationId: string; data?: any }>>([]);
  const [panelHeight, setPanelHeight] = useState(70); // Panel height as vh percentage
  const [isResizing, setIsResizing] = useState(false);
  const pageRef = useRef<HTMLDivElement>(null);
  const resizeRef = useRef<HTMLDivElement>(null);

  // Predefined colors for quick selection
  const colors = [
    { name: 'Yellow', value: '#FFFF00' },
    { name: 'Orange', value: '#FFA500' },
    { name: 'Red', value: '#FF0000' },
    { name: 'Green', value: '#00FF00' },
    { name: 'Blue', value: '#0000FF' },
    { name: 'Purple', value: '#800080' },
    { name: 'Pink', value: '#FF69B4' },
    { name: 'Cyan', value: '#00FFFF' }
  ];

  useEffect(() => {
    if (selectedNodeId) {
      loadPIDDocuments();
    }
  }, [selectedNodeId]);

  useEffect(() => {
    if (selectedPID) {
      loadPIDFile(selectedPID.id);
      loadNodeLocations(selectedPID.id);
    }

    // Cleanup: revoke blob URL when component unmounts or when selectedPID changes
    return () => {
      if (pdfUrl && pdfUrl.startsWith('blob:')) {
        URL.revokeObjectURL(pdfUrl);
      }
    };
  }, [selectedPID]);

  useEffect(() => {
    // Auto-navigate to selected node's location
    if (selectedNodeId && selectedPID && nodeLocations.length > 0) {
      const nodeLocation = nodeLocations.find(loc => loc.node_id === selectedNodeId);
      if (nodeLocation) {
        setCurrentPage(nodeLocation.page_number);
        setIsExpanded(true); // Auto-expand when node is selected
      }
    }
  }, [selectedNodeId, nodeLocations, selectedPID]);

  // Keyboard shortcut for undo (Ctrl+Z / Cmd+Z)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Check for Ctrl+Z (Windows/Linux) or Cmd+Z (Mac)
      if ((e.ctrlKey || e.metaKey) && e.key === 'z') {
        e.preventDefault();
        handleUndo();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [undoStack]); // Re-attach when undoStack changes to capture latest state

  // Handle panel resizing
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!isResizing) return;

      const newHeight = ((window.innerHeight - e.clientY) / window.innerHeight) * 100;
      // Constrain between 20% and 90% of viewport height
      const constrainedHeight = Math.min(Math.max(newHeight, 20), 90);
      setPanelHeight(constrainedHeight);
    };

    const handleMouseUp = () => {
      setIsResizing(false);
    };

    if (isResizing) {
      window.addEventListener('mousemove', handleMouseMove);
      window.addEventListener('mouseup', handleMouseUp);
    }

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isResizing]);

  const loadPIDDocuments = async () => {
    if (!selectedNodeId) return;

    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API_URL}/api/pid/node/${selectedNodeId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setPidDocuments(response.data);
      if (response.data.length > 0 && !selectedPID) {
        setSelectedPID(response.data[0]);
      } else if (response.data.length === 0) {
        setSelectedPID(null);
        setPdfUrl(null);
        setNodeLocations([]);
      }
    } catch (err) {
      console.error('Failed to load P&ID documents:', err);
    }
  };

  const loadPIDFile = async (pidId: string) => {
    try {
      const url = `${API_URL}/api/pid/file/${pidId}`;
      console.log('[PIDViewer] Loading P&ID from URL:', url);

      // Fetch the PDF as a blob to work around CORS/auth issues
      const token = localStorage.getItem('token');
      const response = await axios.get(url, {
        headers: token ? { Authorization: `Bearer ${token}` } : undefined,
        responseType: 'blob'
      });

      console.log('[PIDViewer] Response received:', {
        status: response.status,
        contentType: response.headers['content-type'],
        size: response.data.size
      });

      // Create a blob URL
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const blobUrl = URL.createObjectURL(blob);
      console.log('[PIDViewer] Created blob URL:', blobUrl);
      console.log('[PIDViewer] Blob details:', { size: blob.size, type: blob.type });
      setPdfUrl(blobUrl);
    } catch (err: any) {
      console.error('[PIDViewer] Failed to load PDF file:', err);
      console.error('[PIDViewer] Error details:', {
        message: err.message,
        response: err.response?.data,
        status: err.response?.status
      });
      alert(`Failed to load PDF file: ${err.message}\nCheck console for details.`);
    }
  };

  const loadNodeLocations = async (pidId: string) => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API_URL}/api/pid/location/pid/${pidId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setNodeLocations(response.data);
    } catch (err) {
      console.error('Failed to load node locations:', err);
    }
  };

  const handleUpload = async () => {
    if (!uploadFile || !selectedNodeId) return;

    try {
      const token = localStorage.getItem('token');
      const formData = new FormData();
      formData.append('file', uploadFile);

      // Don't set Content-Type header manually - let axios set it with boundary
      await axios.post(`${API_URL}/api/pid/upload/${selectedNodeId}`, formData, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });

      setShowUploadModal(false);
      setUploadFile(null);
      loadPIDDocuments();
      alert('P&ID uploaded successfully!');
    } catch (err: any) {
      console.error('Failed to upload P&ID:', err);
      const errorMsg = err.response?.data?.detail || err.message || 'Unknown error';
      alert(`Failed to upload PDF: ${errorMsg}\n\nCheck console for details.`);
    }
  };

  const handleDelete = async (pidId: string) => {
    if (!confirm('Delete this P&ID document? This will also remove all node location markers.')) return;

    try {
      const token = localStorage.getItem('token');
      await axios.delete(`${API_URL}/api/pid/${pidId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (selectedPID?.id === pidId) {
        setSelectedPID(null);
        setPdfUrl(null);
      }
      loadPIDDocuments();
    } catch (err) {
      console.error('Failed to delete P&ID:', err);
      alert('Failed to delete P&ID');
    }
  };

  const handleMouseDown = (event: React.MouseEvent<HTMLDivElement>) => {
    if (!selectedPID) return;

    // Don't interfere with resize or existing interactions
    if (resizingHighlight || draggedHighlight) return;

    if (!markingMode || !selectedNodeId) return;

    const rect = event.currentTarget.getBoundingClientRect();
    const x = ((event.clientX - rect.left) / rect.width) * 100;
    const y = ((event.clientY - rect.top) / rect.height) * 100;

    setIsDrawing(true);
    setDrawStart({ x, y });
    setCurrentDraw({ x, y, width: 0, height: 0 });
  };

  const handleMouseMove = (event: React.MouseEvent<HTMLDivElement>) => {
    if (!pageRef.current) return;

    const rect = pageRef.current.getBoundingClientRect();
    const currentX = ((event.clientX - rect.left) / rect.width) * 100;
    const currentY = ((event.clientY - rect.top) / rect.height) * 100;

    // Handle resizing
    if (resizingHighlight) {
      const location = nodeLocations.find(loc => loc.id === resizingHighlight.id);
      if (!location) return;

      const corner = resizingHighlight.corner;
      const left = location.x_coordinate - location.width / 2;
      const top = location.y_coordinate - location.height / 2;
      const right = location.x_coordinate + location.width / 2;
      const bottom = location.y_coordinate + location.height / 2;

      let newLeft = left;
      let newTop = top;
      let newRight = right;
      let newBottom = bottom;

      // Update corners based on which handle is being dragged
      if (corner.includes('w')) newLeft = Math.min(currentX, right - 1);
      if (corner.includes('e')) newRight = Math.max(currentX, left + 1);
      if (corner.includes('n')) newTop = Math.min(currentY, bottom - 1);
      if (corner.includes('s')) newBottom = Math.max(currentY, top + 1);

      const newWidth = Math.abs(newRight - newLeft);
      const newHeight = Math.abs(newBottom - newTop);
      const newX = newLeft + newWidth / 2;
      const newY = newTop + newHeight / 2;

      // Add constraints to prevent runaway sizing
      const maxWidth = 80; // Max 80% of page width
      const maxHeight = 80; // Max 80% of page height
      const minWidth = 1;
      const minHeight = 1;

      const constrainedWidth = Math.min(Math.max(newWidth, minWidth), maxWidth);
      const constrainedHeight = Math.min(Math.max(newHeight, minHeight), maxHeight);

      // Update local state for visual feedback
      setNodeLocations(locs => locs.map(loc =>
        loc.id === resizingHighlight.id
          ? { ...loc, width: constrainedWidth, height: constrainedHeight, x_coordinate: newX, y_coordinate: newY }
          : loc
      ));
      return;
    }

    // Handle dragging
    if (draggedHighlight && dragOffset) {
      const location = nodeLocations.find(loc => loc.id === draggedHighlight);
      if (!location) return;

      const newX = currentX - dragOffset.x;
      const newY = currentY - dragOffset.y;

      // Update local state for visual feedback
      setNodeLocations(locs => locs.map(loc =>
        loc.id === draggedHighlight
          ? { ...loc, x_coordinate: newX, y_coordinate: newY }
          : loc
      ));
      return;
    }

    // Handle drawing new highlight
    if (isDrawing && drawStart && markingMode) {
      const width = Math.abs(currentX - drawStart.x);
      const height = Math.abs(currentY - drawStart.y);
      const x = Math.min(drawStart.x, currentX);
      const y = Math.min(drawStart.y, currentY);

      setCurrentDraw({ x, y, width, height });
    }
  };

  const handleMouseUp = async () => {
    // Save resized highlight
    if (resizingHighlight) {
      const location = nodeLocations.find(loc => loc.id === resizingHighlight.id);
      if (location) {
        await updateHighlight(resizingHighlight.id, {
          width: location.width,
          height: location.height,
          x_coordinate: location.x_coordinate,
          y_coordinate: location.y_coordinate
        });
      }
      setResizingHighlight(null);
      return;
    }

    // Save dragged highlight
    if (draggedHighlight) {
      const location = nodeLocations.find(loc => loc.id === draggedHighlight);
      if (location) {
        await updateHighlight(draggedHighlight, {
          x_coordinate: location.x_coordinate,
          y_coordinate: location.y_coordinate
        });
      }
      setDraggedHighlight(null);
      setDragOffset(null);
      return;
    }

    // Save new highlight
    if (isDrawing && currentDraw && selectedNodeId && selectedPID) {
      // Only save if rectangle has some size
      if (currentDraw.width > 1 && currentDraw.height > 1) {
        try {
          const token = localStorage.getItem('token');
          const response = await axios.post(
            `${API_URL}/api/pid/location`,
            {
              node_id: selectedNodeId,
              pid_document_id: selectedPID.id,
              page_number: currentPage,
              x_coordinate: currentDraw.x + currentDraw.width / 2, // Center point
              y_coordinate: currentDraw.y + currentDraw.height / 2,
              width: currentDraw.width,
              height: currentDraw.height,
              color: selectedColor
            },
            { headers: { Authorization: `Bearer ${token}` } }
          );

          // Track for undo
          setUndoStack(prev => [...prev, {
            action: 'create',
            locationId: response.data.id
          }].slice(-20));

          loadNodeLocations(selectedPID.id);
          onNodeMarked?.();
        } catch (err) {
          console.error('Failed to mark location:', err);
          alert('Failed to mark location');
        }
      }

      setIsDrawing(false);
      setDrawStart(null);
      setCurrentDraw(null);
    }
  };

  const handleDeleteHighlight = async (locationId: string) => {
    if (!confirm('Delete this highlight?')) return;

    const location = nodeLocations.find(loc => loc.id === locationId);
    if (!location) return;

    // Track for undo
    setUndoStack(prev => [...prev, {
      action: 'delete',
      locationId,
      data: { ...location }
    }].slice(-20));

    try {
      const token = localStorage.getItem('token');
      await axios.delete(`${API_URL}/api/pid/location/${locationId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (selectedPID) {
        loadNodeLocations(selectedPID.id);
      }
    } catch (err) {
      console.error('Failed to delete highlight:', err);
      alert('Failed to delete highlight');
    }
  };

  const updateHighlight = async (locationId: string, updates: Partial<NodeLocation>, trackUndo = true) => {
    const location = nodeLocations.find(loc => loc.id === locationId);
    if (!location) return;

    // Track undo before making changes
    if (trackUndo) {
      setUndoStack(prev => [...prev, {
        action: 'update',
        locationId,
        data: { ...location }
      }].slice(-20)); // Keep last 20 actions
    }

    try {
      const token = localStorage.getItem('token');
      await axios.post(
        `${API_URL}/api/pid/location`,
        {
          node_id: location.node_id,
          pid_document_id: location.pid_document_id,
          page_number: location.page_number,
          x_coordinate: updates.x_coordinate ?? location.x_coordinate,
          y_coordinate: updates.y_coordinate ?? location.y_coordinate,
          width: updates.width ?? location.width,
          height: updates.height ?? location.height,
          color: updates.color ?? location.color
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      // Delete old one
      await axios.delete(`${API_URL}/api/pid/location/${locationId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (selectedPID) {
        loadNodeLocations(selectedPID.id);
      }
    } catch (err) {
      console.error('Failed to update highlight:', err);
    }
  };

  const handleUndo = async () => {
    if (undoStack.length === 0) return;

    const lastAction = undoStack[undoStack.length - 1];
    setUndoStack(prev => prev.slice(0, -1));

    try {
      const token = localStorage.getItem('token');

      if (lastAction.action === 'create') {
        // Undo create: delete the highlight
        await axios.delete(`${API_URL}/api/pid/location/${lastAction.locationId}`, {
          headers: { Authorization: `Bearer ${token}` }
        });
      } else if (lastAction.action === 'delete') {
        // Undo delete: recreate the highlight
        await axios.post(
          `${API_URL}/api/pid/location`,
          lastAction.data,
          { headers: { Authorization: `Bearer ${token}` } }
        );
      } else if (lastAction.action === 'update') {
        // Undo update: restore previous state (without tracking undo)
        await updateHighlight(lastAction.locationId, lastAction.data, false);
      }

      if (selectedPID) {
        loadNodeLocations(selectedPID.id);
      }
    } catch (err) {
      console.error('Failed to undo:', err);
      alert('Failed to undo action');
    }
  };

  const onDocumentLoadSuccess = ({ numPages }: { numPages: number }) => {
    setNumPages(numPages);
  };

  // Memoize the file prop to avoid unnecessary reloads
  // The PDF is loaded as a blob URL, so just pass it directly
  const pdfFileConfig = useMemo(() => {
    if (!pdfUrl) return null;
    return pdfUrl;
  }, [pdfUrl]);

  // Upload Modal Component
  const renderUploadModal = () => (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <h2 className="text-xl font-bold mb-4">Upload P&ID Document</h2>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Select PDF file:</label>
            <input
              type="file"
              accept=".pdf"
              onChange={(e) => setUploadFile(e.target.files?.[0] || null)}
              className="w-full border rounded px-3 py-2"
            />
          </div>
          <div className="flex justify-end gap-2">
            <button
              onClick={() => {
                setShowUploadModal(false);
                setUploadFile(null);
              }}
              className="px-4 py-2 border rounded hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              onClick={handleUpload}
              disabled={!uploadFile}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
            >
              Upload
            </button>
          </div>
        </div>
      </div>
    </div>
  );

  // Don't show P&ID panel if no node is selected
  if (!selectedNodeId) {
    return <>{showUploadModal && renderUploadModal()}</>;
  }

  // If no P&IDs uploaded, show compact upload button (only when node is selected)
  if (pidDocuments.length === 0) {
    return (
      <>
        <div className="fixed bottom-0 left-0 right-0 bg-white border-t px-4 py-3 flex items-center justify-between shadow-lg z-40">
          <span className="text-sm text-gray-600">📄 No P&ID documents for this node - Upload P&IDs to mark locations</span>
          <button
            onClick={() => setShowUploadModal(true)}
            className="text-sm bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700"
          >
            + Upload P&ID for This Node
          </button>
        </div>
        {showUploadModal && renderUploadModal()}
      </>
    );
  }

  // Check if current node has markers on the currently displayed P&ID
  const currentNodeHasMarkersOnThisPID = nodeLocations.some(loc => loc.node_id === selectedNodeId);

  return (
    <>
      {/* Cursor overlay during resize to prevent flickering */}
      {isResizing && (
        <div
          className="fixed inset-0 z-50"
          style={{ cursor: 'ns-resize' }}
        />
      )}

      {/* Resize handle */}
      <div
        ref={resizeRef}
        className={`fixed left-0 right-0 bg-gray-300 hover:bg-blue-500 transition-colors z-50 ${
          isResizing ? 'bg-blue-500' : ''
        }`}
        style={{
          bottom: isExpanded ? `${panelHeight}vh` : 'auto',
          top: !isExpanded ? 'auto' : undefined,
          height: '4px',
          cursor: 'ns-resize',
          display: isExpanded ? 'block' : 'none'
        }}
        onMouseDown={() => setIsResizing(true)}
        title="Drag to resize panel"
      />

      <div
        className="fixed bottom-0 left-0 right-0 bg-white border-t shadow-lg z-40"
        style={{
          height: isExpanded ? `${panelHeight}vh` : 'auto',
          transition: isResizing ? 'none' : 'all 0.3s'
        }}
      >
        {/* Collapsed Header Bar */}
        {!isExpanded && (
          <div className="px-4 py-3 flex items-center justify-between cursor-pointer hover:bg-gray-50" onClick={() => setIsExpanded(true)}>
            <div className="flex items-center gap-3">
              <span className="font-semibold text-gray-900">📄 P&ID:</span>
              {selectedPID && (
                <div className="flex items-center gap-2">
                  <span className="text-sm text-gray-600">{selectedPID.filename}</span>
                  <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded">
                    {numPages} pages
                  </span>
                  {!currentNodeHasMarkersOnThisPID && (
                    <span className="text-xs bg-amber-100 text-amber-700 px-2 py-1 rounded">
                      No markers on this P&ID - Click to add
                    </span>
                  )}
                </div>
              )}
            </div>
            <div className="flex items-center gap-2">
              <span className="text-xs text-gray-500">Click to expand</span>
              <span className="text-xl">▲</span>
            </div>
          </div>
        )}

        {/* Expanded View */}
        {isExpanded && (
          <div className="h-full flex flex-col">
            {/* Header */}
            <div className="bg-white border-b px-4 py-2 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <button
                  onClick={() => setIsExpanded(false)}
                  className="text-gray-600 hover:text-gray-900"
                  title="Collapse"
                >
                  <span className="text-xl">▼</span>
                </button>
                <h3 className="font-semibold text-gray-900">📄 P&ID Viewer</h3>
                {selectedPID && (
                  <div className="flex items-center gap-2">
                    <select
                      value={selectedPID.id}
                      onChange={(e) => {
                        const pid = pidDocuments.find(p => p.id === e.target.value);
                        if (pid) setSelectedPID(pid);
                      }}
                      className="text-sm border rounded px-2 py-1"
                    >
                      {pidDocuments.map(pid => (
                        <option key={pid.id} value={pid.id}>{pid.filename}</option>
                      ))}
                    </select>
                    <button
                      onClick={() => selectedPID && handleDelete(selectedPID.id)}
                      className="text-red-600 hover:text-red-800 text-sm px-2 py-1"
                      title="Delete P&ID"
                    >
                      🗑️
                    </button>
                  </div>
                )}
              </div>

              <div className="flex gap-2 items-center">
                {selectedNodeId && selectedPID && (
                  <>
                    <button
                      onClick={() => setMarkingMode(!markingMode)}
                      className={`text-sm px-3 py-1 rounded ${
                        markingMode
                          ? 'bg-green-600 text-white'
                          : 'bg-gray-200 hover:bg-gray-300'
                      }`}
                    >
                      {markingMode ? '✓ Drag to highlight' : '🖍️ Highlight Mode'}
                    </button>
                    {markingMode && (
                      <>
                        <div className="flex gap-1 border-l pl-2">
                          {colors.map((color) => (
                            <button
                              key={color.value}
                              onClick={() => setSelectedColor(color.value)}
                              className={`w-6 h-6 rounded border-2 ${
                                selectedColor === color.value ? 'border-gray-900 ring-2 ring-gray-400' : 'border-gray-300'
                              }`}
                              style={{ backgroundColor: color.value }}
                              title={color.name}
                            />
                          ))}
                        </div>
                        <input
                          type="color"
                          value={selectedColor}
                          onChange={(e) => setSelectedColor(e.target.value)}
                          className="w-8 h-6 border rounded cursor-pointer"
                          title="Custom color"
                        />
                      </>
                    )}
                    <button
                      onClick={handleUndo}
                      disabled={undoStack.length === 0}
                      className="text-sm px-3 py-1 rounded bg-gray-200 hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed"
                      title={`Undo (${undoStack.length} actions)`}
                    >
                      ↶ Undo
                    </button>
                  </>
                )}
                <button
                  onClick={() => setShowUploadModal(true)}
                  className="text-sm bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700"
                >
                  + Upload
                </button>
              </div>
            </div>

            {/* PDF Viewer */}
            {selectedPID && pdfUrl ? (
              <div className="flex-1 overflow-auto p-4 bg-gray-50">
                <div
                  ref={pageRef}
                  onMouseDown={handleMouseDown}
                  onMouseMove={handleMouseMove}
                  onMouseUp={handleMouseUp}
                  onMouseLeave={handleMouseUp}
                  className={`relative inline-block ${markingMode ? 'cursor-crosshair' : 'cursor-default'} select-none`}
                  style={{ position: 'relative', userSelect: 'none' }}
                >
                  <Document
                    file={pdfFileConfig}
                    onLoadSuccess={onDocumentLoadSuccess}
                    onLoadError={(error) => {
                      console.error('[PIDViewer] PDF load error:', error);
                      console.error('[PIDViewer] PDF URL:', pdfUrl);
                      console.error('[PIDViewer] PDF config:', pdfFileConfig);
                      console.error('[PIDViewer] Error name:', error.name);
                      console.error('[PIDViewer] Error message:', error.message);
                      if (error.name === 'MissingPDFException') {
                        console.error('[PIDViewer] The PDF file appears to be empty or corrupt');
                      }
                      alert(`PDF Loading Failed!\n\nError: ${error.message}\nType: ${error.name}\n\nCheck browser console for full details.`);
                    }}
                    loading={<div className="text-center py-8">Loading PDF...</div>}
                    error={
                      <div className="text-center py-8 text-red-600">
                        <div className="mb-2">Failed to load PDF</div>
                        <div className="text-sm text-gray-600">URL: {pdfUrl}</div>
                        <div className="text-xs text-gray-500 mt-2">Check browser console for details</div>
                      </div>
                    }
                  >
                    <Page
                      pageNumber={currentPage}
                      renderTextLayer={false}
                      renderAnnotationLayer={false}
                      width={Math.min(window.innerWidth * 0.9, 1200)}
                    />
                  </Document>

                  {/* Render node highlight markers */}
                  {nodeLocations
                    .filter(loc => loc.page_number === currentPage)
                    .map(loc => (
                      <div
                        key={loc.id}
                        className="absolute group"
                        style={{
                          left: `${loc.x_coordinate - loc.width / 2}%`,
                          top: `${loc.y_coordinate - loc.height / 2}%`,
                          width: `${loc.width}%`,
                          height: `${loc.height}%`,
                          backgroundColor: loc.color,
                          opacity: hoveredHighlight === loc.id ? 0.6 : (loc.node_id === selectedNodeId ? 0.5 : 0.35),
                          zIndex: hoveredHighlight === loc.id ? 30 : (loc.node_id === selectedNodeId ? 20 : 10),
                          pointerEvents: markingMode ? 'none' : 'auto',
                          cursor: draggedHighlight === loc.id ? 'grabbing' : (resizingHighlight?.id === loc.id ? 'default' : 'grab')
                        }}
                        onMouseEnter={() => !markingMode && setHoveredHighlight(loc.id)}
                        onMouseLeave={() => !draggedHighlight && !resizingHighlight && setHoveredHighlight(null)}
                        onMouseDown={(e) => {
                          if (markingMode) return;

                          // Check if clicking on a resize handle - if so, don't start drag
                          const target = e.target as HTMLElement;
                          if (target.classList.contains('resize-handle')) return;

                          e.stopPropagation();
                          const rect = pageRef.current?.getBoundingClientRect();
                          if (!rect) return;
                          const clickX = ((e.clientX - rect.left) / rect.width) * 100;
                          const clickY = ((e.clientY - rect.top) / rect.height) * 100;
                          setDraggedHighlight(loc.id);
                          setDragOffset({
                            x: clickX - loc.x_coordinate,
                            y: clickY - loc.y_coordinate
                          });
                        }}
                        title={`Highlight (${loc.color}) - Drag to move`}
                      >
                        {/* Delete button */}
                        {hoveredHighlight === loc.id && !markingMode && (
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              handleDeleteHighlight(loc.id);
                            }}
                            onMouseDown={(e) => e.stopPropagation()}
                            className="absolute -top-2 -right-2 bg-red-600 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs hover:bg-red-700 shadow-lg z-50"
                            title="Delete highlight"
                          >
                            ✕
                          </button>
                        )}

                        {/* Resize handles */}
                        {hoveredHighlight === loc.id && !markingMode && (
                          <>
                            {['nw', 'ne', 'sw', 'se'].map(corner => (
                              <div
                                key={corner}
                                className="resize-handle absolute w-3 h-3 bg-blue-600 border border-white rounded-full cursor-pointer hover:bg-blue-700"
                                style={{
                                  [corner.includes('n') ? 'top' : 'bottom']: '-6px',
                                  [corner.includes('w') ? 'left' : 'right']: '-6px',
                                  cursor: `${corner}-resize`,
                                  zIndex: 40
                                }}
                                onMouseDown={(e) => {
                                  e.stopPropagation();
                                  setResizingHighlight({ id: loc.id, corner });
                                }}
                                title={`Resize ${corner}`}
                              />
                            ))}
                          </>
                        )}
                      </div>
                    ))}

                  {/* Show current drawing rectangle */}
                  {isDrawing && currentDraw && (
                    <div
                      className="absolute pointer-events-none"
                      style={{
                        left: `${currentDraw.x}%`,
                        top: `${currentDraw.y}%`,
                        width: `${currentDraw.width}%`,
                        height: `${currentDraw.height}%`,
                        backgroundColor: selectedColor,
                        opacity: 0.5,
                        zIndex: 50,
                        outline: '2px dashed rgba(59, 130, 246, 0.8)',
                        outlineOffset: '-2px'
                      }}
                    />
                  )}
                </div>

                {/* Page Navigation */}
                <div className="flex justify-center items-center gap-4 mt-4">
                  <button
                    onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                    disabled={currentPage <= 1}
                    className="px-3 py-1 bg-gray-200 rounded hover:bg-gray-300 disabled:opacity-50"
                  >
                    ← Previous
                  </button>
                  <span className="text-sm text-gray-600">
                    Page {currentPage} of {numPages}
                  </span>
                  <button
                    onClick={() => setCurrentPage(Math.min(numPages, currentPage + 1))}
                    disabled={currentPage >= numPages}
                    className="px-3 py-1 bg-gray-200 rounded hover:bg-gray-300 disabled:opacity-50"
                  >
                    Next →
                  </button>
                </div>
              </div>
            ) : (
              <div className="flex-1 flex items-center justify-center text-gray-500 bg-gray-50">
                <p>Loading P&ID...</p>
              </div>
            )}
          </div>
        )}
      </div>

      {showUploadModal && renderUploadModal()}
    </>
  );
};
