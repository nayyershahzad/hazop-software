import { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface RegulationReference {
  title: string;
  description: string;
  source: string;
  relevance: string;
  link?: string;
}

interface IncidentReport {
  title: string;
  description: string;
  date: string;
  facility: string;
  relevance: string;
}

interface TechnicalReference {
  title: string;
  description: string;
  source: string;
  relevance: string;
}

interface IndustryBenchmark {
  title: string;
  description: string;
  value: string;
  source: string;
}

interface ContextualKnowledge {
  regulations: RegulationReference[];
  incident_reports: IncidentReport[];
  technical_references: TechnicalReference[];
  industry_benchmarks: IndustryBenchmark[];
}

interface ContextualKnowledgePanelProps {
  nodeId: string;
  deviationId?: string;
  nodeName: string;
  deviationDescription?: string;
}

export const ContextualKnowledgePanel = ({
  nodeId,
  deviationId,
  nodeName,
  deviationDescription
}: ContextualKnowledgePanelProps) => {
  const [isOpen, setIsOpen] = useState(false);
  const [activeTab, setActiveTab] = useState<'regulations' | 'incidents' | 'technical' | 'benchmarks'>('regulations');
  const [knowledge, setKnowledge] = useState<ContextualKnowledge | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const fetchContextualKnowledge = async () => {
    if (!nodeId) return;

    setIsLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        `${API_URL}/api/gemini/contextual-knowledge`,
        {
          node_id: nodeId,
          deviation_id: deviationId
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setKnowledge(response.data);
    } catch (err) {
      console.error('Failed to fetch contextual knowledge:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen && !knowledge) {
      fetchContextualKnowledge();
    }
  }, [isOpen, nodeId, deviationId]);

  const getItemCount = () => {
    if (!knowledge) return 0;

    return knowledge.regulations.length +
           knowledge.incident_reports.length +
           knowledge.technical_references.length +
           knowledge.industry_benchmarks.length;
  };

  const toggle = () => {
    setIsOpen(!isOpen);
  };

  const getTabClassName = (tab: string) => {
    return `px-3 py-2 text-sm font-medium ${activeTab === tab ?
      'border-b-2 border-purple-600 text-purple-600' :
      'text-gray-500 hover:text-gray-700 hover:border-gray-300 border-b-2 border-transparent'}`;
  };

  return (
    <div className="bg-white rounded-lg shadow mt-4">
      {/* Header */}
      <div
        className="flex items-center justify-between p-4 cursor-pointer"
        onClick={toggle}
      >
        <div className="flex items-center gap-2">
          <span role="img" aria-label="Knowledge" className="text-purple-600 text-lg">📚</span>
          <h3 className="font-medium text-gray-900">Contextual Knowledge</h3>
          {getItemCount() > 0 && (
            <span className="bg-purple-100 text-purple-800 text-xs font-medium rounded-full px-2 py-0.5">
              {getItemCount()} references
            </span>
          )}
        </div>
        <button className="text-gray-400 hover:text-gray-500">
          {isOpen ? '▲' : '▼'}
        </button>
      </div>

      {/* Panel Content */}
      {isOpen && (
        <div className="border-t border-gray-200 p-4">
          {isLoading ? (
            <div className="text-center py-8">
              <div className="animate-spin h-5 w-5 border-2 border-purple-600 border-t-transparent rounded-full mx-auto mb-2"></div>
              <p className="text-gray-600 text-sm">Gathering contextual information...</p>
            </div>
          ) : knowledge ? (
            <div>
              <p className="text-gray-500 text-sm mb-4">
                Context-sensitive information related to {nodeName}
                {deviationDescription && ` - ${deviationDescription}`}
              </p>

              {/* Tabs */}
              <div className="border-b border-gray-200 mb-4">
                <nav className="flex -mb-px">
                  <button
                    className={getTabClassName('regulations')}
                    onClick={() => setActiveTab('regulations')}
                  >
                    Regulations {knowledge.regulations.length > 0 && `(${knowledge.regulations.length})`}
                  </button>
                  <button
                    className={getTabClassName('incidents')}
                    onClick={() => setActiveTab('incidents')}
                  >
                    Incidents {knowledge.incident_reports.length > 0 && `(${knowledge.incident_reports.length})`}
                  </button>
                  <button
                    className={getTabClassName('technical')}
                    onClick={() => setActiveTab('technical')}
                  >
                    Technical {knowledge.technical_references.length > 0 && `(${knowledge.technical_references.length})`}
                  </button>
                  <button
                    className={getTabClassName('benchmarks')}
                    onClick={() => setActiveTab('benchmarks')}
                  >
                    Benchmarks {knowledge.industry_benchmarks.length > 0 && `(${knowledge.industry_benchmarks.length})`}
                  </button>
                </nav>
              </div>

              {/* Regulations Tab Content */}
              {activeTab === 'regulations' && (
                <div className="space-y-4">
                  {knowledge.regulations.length === 0 ? (
                    <p className="text-gray-500 text-sm italic text-center py-4">
                      No relevant regulations found
                    </p>
                  ) : (
                    knowledge.regulations.map((regulation, index) => (
                      <div key={index} className="bg-blue-50 border border-blue-200 rounded-md p-3">
                        <h4 className="font-medium text-blue-800 text-sm">{regulation.title}</h4>
                        <p className="text-gray-600 text-sm mt-1">{regulation.description}</p>
                        <div className="flex flex-wrap gap-2 mt-2 text-xs">
                          <span className="bg-blue-100 text-blue-800 px-2 py-0.5 rounded-full">
                            {regulation.source}
                          </span>
                          <span className="text-gray-500">
                            Relevance: {regulation.relevance}
                          </span>
                        </div>
                        {regulation.link && (
                          <a
                            href={regulation.link}
                            target="_blank"
                            rel="noreferrer"
                            className="text-blue-600 hover:text-blue-800 text-xs flex items-center mt-2"
                          >
                            🔗 View Source
                          </a>
                        )}
                      </div>
                    ))
                  )}
                </div>
              )}

              {/* Incidents Tab Content */}
              {activeTab === 'incidents' && (
                <div className="space-y-4">
                  {knowledge.incident_reports.length === 0 ? (
                    <p className="text-gray-500 text-sm italic text-center py-4">
                      No similar incidents found
                    </p>
                  ) : (
                    knowledge.incident_reports.map((incident, index) => (
                      <div key={index} className="bg-red-50 border border-red-200 rounded-md p-3">
                        <h4 className="font-medium text-red-800 text-sm">{incident.title}</h4>
                        <p className="text-gray-600 text-sm mt-1">{incident.description}</p>
                        <div className="flex flex-wrap gap-2 mt-2 text-xs">
                          <span className="bg-red-100 text-red-800 px-2 py-0.5 rounded-full">
                            {incident.date}
                          </span>
                          <span className="bg-red-100 text-red-800 px-2 py-0.5 rounded-full">
                            {incident.facility}
                          </span>
                        </div>
                        <p className="text-gray-500 text-xs mt-2">
                          Relevance: {incident.relevance}
                        </p>
                      </div>
                    ))
                  )}
                </div>
              )}

              {/* Technical Tab Content */}
              {activeTab === 'technical' && (
                <div className="space-y-4">
                  {knowledge.technical_references.length === 0 ? (
                    <p className="text-gray-500 text-sm italic text-center py-4">
                      No technical references found
                    </p>
                  ) : (
                    knowledge.technical_references.map((reference, index) => (
                      <div key={index} className="bg-green-50 border border-green-200 rounded-md p-3">
                        <h4 className="font-medium text-green-800 text-sm">{reference.title}</h4>
                        <p className="text-gray-600 text-sm mt-1">{reference.description}</p>
                        <div className="flex flex-wrap gap-2 mt-2 text-xs">
                          <span className="bg-green-100 text-green-800 px-2 py-0.5 rounded-full">
                            {reference.source}
                          </span>
                          <span className="text-gray-500">
                            Relevance: {reference.relevance}
                          </span>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              )}

              {/* Benchmarks Tab Content */}
              {activeTab === 'benchmarks' && (
                <div className="space-y-4">
                  {knowledge.industry_benchmarks.length === 0 ? (
                    <p className="text-gray-500 text-sm italic text-center py-4">
                      No industry benchmarks found
                    </p>
                  ) : (
                    knowledge.industry_benchmarks.map((benchmark, index) => (
                      <div key={index} className="bg-yellow-50 border border-yellow-200 rounded-md p-3">
                        <h4 className="font-medium text-yellow-800 text-sm">{benchmark.title}</h4>
                        <p className="text-gray-600 text-sm mt-1">{benchmark.description}</p>
                        <div className="flex flex-wrap gap-2 mt-2 text-xs">
                          <span className="bg-yellow-100 text-yellow-800 px-2 py-1 rounded font-medium">
                            Value: {benchmark.value}
                          </span>
                          <span className="text-gray-500 mt-1">
                            Source: {benchmark.source}
                          </span>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-8">
              <p className="text-gray-500 text-sm">Click the button below to load contextual knowledge</p>
              <button
                onClick={fetchContextualKnowledge}
                className="mt-3 bg-purple-600 hover:bg-purple-700 text-white text-sm px-4 py-2 rounded"
              >
                Load Knowledge
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};