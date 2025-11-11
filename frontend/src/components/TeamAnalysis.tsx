import React, { useState, useEffect } from 'react';
import './TeamAnalysis.css';

interface TeamData {
  team_id: number;
  team_name: string;
  manager_name: string;
  current_rank: number;
  total_points: number;
  current_gameweek: number;
  transfers_remaining: number;
  transfer_bank: number;
}

interface Player {
  player_id: number;
  name: string;
  team: string;
  position: string;
  price: number;
  form: number;
  selected_by_percent: number;
  expected_points_this_week?: number;
  upcoming_fdr?: number;
  score: number;
  reason: string;
  photo_url?: string;
}

interface Recommendations {
  GK: Player[];
  DEF: Player[];
  MID: Player[];
  FWD: Player[];
}

interface Differential {
  player_id: number;
  name: string;
  team: string;
  position: string;
  price: number;
  form: number;
  selected_by_percent: number;
  differential_score: number;
  reason: string;
  photo_url?: string;
}

interface SquadOverview {
  total_spent: number;
  bank: number;
  squad_form: number;
  squad: Array<{
    player_id: number;
    name: string;
    team: string;
    position: string;
    price: number;
    form: number;
    points_per_million: number;
    performance_rating: string;
  }>;
}

interface SwapOption {
  name: string;
  team: string;
  price: number;
  reason: string;
  photo_url?: string;
}

interface SwapData {
  swap_out: {
    name: string;
    price: number;
    reason: string;
    photo_url?: string;
  };
  swap_in_options: SwapOption[];
}

interface SmartSwaps {
  smart_swaps: {
    [position: string]: SwapData[];
  };
}

interface TeamAnalysisProps {
  teamData: TeamData;
}

const TeamAnalysis: React.FC<TeamAnalysisProps> = ({ teamData }) => {
  const [recommendations, setRecommendations] = useState<Recommendations | null>(null);
  const [differentials, setDifferentials] = useState<Record<string, Differential[]> | Differential[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'squad' | 'transfers' | 'differentials' | 'swaps'>('overview');
  const [squadData, setSquadData] = useState<SquadOverview | null>(null);
  const [swapsData, setSwapsData] = useState<SmartSwaps | null>(null);

  useEffect(() => {
    fetchRecommendations();
  }, [teamData.team_id]);

  const fetchRecommendations = async () => {
    setLoading(true);
    setError(null);
    try {
      const [transResponse, diffResponse] = await Promise.all([
        fetch(`http://localhost:5000/api/recommendations/${teamData.team_id}/transfers`),
        fetch(`http://localhost:5000/api/recommendations/${teamData.team_id}/differentials`)
      ]);

      if (!transResponse.ok || !diffResponse.ok) {
        throw new Error('Failed to fetch recommendations');
      }

      const transData = await transResponse.json();
      const diffData = await diffResponse.json();

      setRecommendations(transData.recommendations);
      setDifferentials(diffData.differentials);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load recommendations');
    } finally {
      setLoading(false);
    }
  };

  const fetchSquadData = async () => {
    try {
      const response = await fetch(`http://localhost:5000/api/team/${teamData.team_id}/squad-overview`);
      if (!response.ok) throw new Error('Failed to fetch squad');
      const data = await response.json();
      setSquadData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load squad');
    }
  };

  const fetchSwapsData = async () => {
    try {
      const response = await fetch(`http://localhost:5000/api/team/${teamData.team_id}/smart-swaps`);
      if (!response.ok) throw new Error('Failed to fetch swaps');
      const data = await response.json();
      setSwapsData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load swaps');
    }
  };

  return (
    <div className="team-analysis">
      <div className="team-header">
        <h2>{teamData.team_name}</h2>
        <p className="manager">Manager: {teamData.manager_name}</p>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">Total Points</div>
          <div className="stat-value">{teamData.total_points}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Overall Rank</div>
          <div className="stat-value">#{teamData.current_rank?.toLocaleString()}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Current Gameweek</div>
          <div className="stat-value">GW{teamData.current_gameweek}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Transfers Available</div>
          <div className="stat-value">{teamData.transfers_remaining}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Transfer Bank</div>
          <div className="stat-value">£{teamData.transfer_bank.toFixed(1)}m</div>
        </div>
      </div>

      <div className="tabs">
        <button
          className={`tab-button ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          Overview
        </button>
        <button
          className={`tab-button ${activeTab === 'squad' ? 'active' : ''}`}
          onClick={() => { setActiveTab('squad'); fetchSquadData(); }}
        >
          Squad
        </button>
        <button
          className={`tab-button ${activeTab === 'swaps' ? 'active' : ''}`}
          onClick={() => { setActiveTab('swaps'); fetchSwapsData(); }}
        >
          Smart Swaps
        </button>
        <button
          className={`tab-button ${activeTab === 'transfers' ? 'active' : ''}`}
          onClick={() => setActiveTab('transfers')}
        >
          Best Transfers
        </button>
        <button
          className={`tab-button ${activeTab === 'differentials' ? 'active' : ''}`}
          onClick={() => setActiveTab('differentials')}
        >
          Differentials
        </button>
      </div>

      <div className="tab-content">
        {activeTab === 'overview' && (
          <div className="overview-section">
            <p>Select "Squad" to view your current team with performance ratings.</p>
            <p>Select "Smart Swaps" to get specific player swap recommendations.</p>
            <p>Select "Best Transfers" to see optimized transfer recommendations per position.</p>
            <p>Select "Differentials" to discover low-ownership players with high potential.</p>
          </div>
        )}

        {activeTab === 'squad' && (
          <div className="squad-section">
            {squadData ? (
              <>
                <div className="squad-summary">
                  <p>Total Spent: £{squadData.total_spent.toFixed(1)}m</p>
                  <p>In Bank: £{squadData.bank.toFixed(1)}m</p>
                  <p>Squad Form: {squadData.squad_form.toFixed(2)}</p>
                </div>
                {['GK', 'DEF', 'MID', 'FWD'].map((position) => {
                  const posPlayers = squadData.squad.filter((p: any) => p.position === position);
                  return (
                    <div key={position} className="position-group">
                      <h4>{position} ({posPlayers.length})</h4>
                      <div className="players-grid">
                        {posPlayers.map((player: { player_id: number; name: string; team: string; position: string; price: number; form: number; points_per_million: number; performance_rating: string; photo_url?: string }) => (
                          <div key={player.player_id} className={`squad-player ${player.performance_rating.toLowerCase()}`}>
                            {player.photo_url && <img src={player.photo_url} alt={player.name} className="player-photo" />}
                            <div className="player-name">{player.name}</div>
                            <div className="player-team">{player.team}</div>
                            <div className="player-price">£{player.price.toFixed(1)}m</div>
                            <div className="player-form">Form: {player.form}</div>
                            <div className="player-value">{player.points_per_million.toFixed(2)} pts/£m</div>
                            <div className="player-rating">{player.performance_rating}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  );
                })}
              </>
            ) : (
              <p className="loading">Loading squad data...</p>
            )}
          </div>
        )}

        {activeTab === 'swaps' && (
          <div className="swaps-section">
            {swapsData ? (
              <>
                {Object.entries(swapsData.smart_swaps as Record<string, SwapData[]>).map(([position, posSwaps]: [string, SwapData[]]) => (
                  <div key={position} className="position-swaps">
                    <h4>{position}</h4>
                    {posSwaps.length > 0 ? (
                      posSwaps.map((swap: SwapData, idx: number) => (
                        <div key={idx} className="swap-card">
                          <div className="swap-out">
                            <strong>Remove:</strong> {swap.swap_out.name}
                            {swap.swap_out.photo_url && <img src={swap.swap_out.photo_url} alt={swap.swap_out.name} className="player-photo" style={{ width: '80px', height: '80px', borderRadius: '8px', margin: '8px 0' }} onError={(e) => { e.currentTarget.style.display = 'none'; }} />}
                            <div className="swap-details">£{swap.swap_out.price.toFixed(1)}m | {swap.swap_out.reason}</div>
                          </div>
                          <div className="swap-arrow">⟶</div>
                          <div className="swap-replacements">
                            <strong>Add:</strong>
                            {swap.swap_in_options.map((opt: SwapOption, oidx: number) => (
                              <div key={oidx} className="replacement-option">
                                {opt.photo_url && <img src={opt.photo_url} alt={opt.name} className="player-photo" style={{ width: '80px', height: '80px', borderRadius: '8px', margin: '4px 0' }} onError={(e) => { e.currentTarget.style.display = 'none'; }} />}
                                {opt.name} ({opt.team}) - £{opt.price.toFixed(1)}m
                                <div className="replacement-reason">{opt.reason}</div>
                              </div>
                            ))}
                          </div>
                        </div>
                      ))
                    ) : (
                      <p>No suggested swaps for {position} - Squad looks great!</p>
                    )}
                  </div>
                ))}
              </>
            ) : (
              <p className="loading">Loading smart swaps...</p>
            )}
          </div>
        )}

        {activeTab === 'transfers' && (
          <div className="transfers-section">
            {loading ? (
              <p className="loading">Loading recommendations...</p>
            ) : error ? (
              <p className="error">Error: {error}</p>
            ) : recommendations ? (
              <div className="positions-grid">
                {(['GK', 'DEF', 'MID', 'FWD']).map((position) => (
                  <div key={position} className="position-card">
                    <h3>{position}</h3>
                    <div className="players-list">
                      {(recommendations[position as keyof Recommendations] || []).map((player: Player) => (
                        <div key={player.player_id} className="player-item">
                          {player.photo_url && <img src={player.photo_url} alt={player.name} className="player-photo" style={{ marginBottom: '8px', width: '100%' }} onError={(e) => { e.currentTarget.style.display = 'none'; }} />}
                          <div className="player-header">
                            <span className="player-name">{player.name}</span>
                            <span className="player-score">{player.score.toFixed(1)}</span>
                          </div>
                          <div className="player-details">
                            <span className="badge">{player.team}</span>
                            <span className="price">£{player.price.toFixed(1)}m</span>
                            <span className="form">Form: {player.form.toFixed(1)}</span>
                            <span className="ownership">{player.selected_by_percent.toFixed(1)}% owned</span>
                          </div>
                          <p className="reason">{player.reason}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            ) : null}
          </div>
        )}

        {activeTab === 'differentials' && (
          <div className="differentials-section">
            {loading ? (
              <p className="loading">Loading differentials...</p>
            ) : error ? (
              <p className="error">Error: {error}</p>
            ) : differentials && Object.keys(differentials).length > 0 ? (
              <div>
                {(['GK', 'DEF', 'MID', 'FWD']).map((position) => {
                  const posPlayers = (differentials as Record<string, Differential[]>)[position] || [];
                  return (
                    <div key={position}>
                      <h3 style={{ color: '#667eea', marginTop: '20px', marginBottom: '15px', borderBottom: '2px solid #667eea', paddingBottom: '10px' }}>
                        {position} - Top Differentials
                      </h3>
                      <div className="differentials-list">
                        {posPlayers.map((player: Differential) => (
                          <div key={player.player_id} className="differential-item">
                            {player.photo_url && <img src={player.photo_url} alt={player.name} className="player-photo" style={{ width: '100%', height: 'auto', borderRadius: '12px 12px 0 0' }} onError={(e) => { e.currentTarget.style.display = 'none'; }} />}
                            <div className="diff-header">
                              <span className="player-name">{player.name}</span>
                              <span className="diff-score">{player.differential_score.toFixed(1)}</span>
                            </div>
                            <div className="diff-details">
                              <span className="badge">{player.team}</span>
                              <span className="price">£{player.price.toFixed(1)}m</span>
                              <span className="form">Form: {player.form.toFixed(1)}</span>
                              <span className="ownership low-ownership">{player.selected_by_percent.toFixed(1)}% owned</span>
                            </div>
                            <p className="reason">{player.reason}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : null}
          </div>
        )}
      </div>
    </div>
  );
};

export default TeamAnalysis;
