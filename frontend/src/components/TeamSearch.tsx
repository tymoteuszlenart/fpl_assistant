import React, { useState } from 'react';
import './TeamSearch.css';

interface TeamSearchProps {
  onTeamSelect: (teamId: number) => void;
  loading: boolean;
}

const TeamSearch: React.FC<TeamSearchProps> = ({ onTeamSelect, loading }) => {
  const [teamId, setTeamId] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (teamId.trim()) {
      onTeamSelect(parseInt(teamId, 10));
    }
  };

  return (
    <div className="team-search">
      <form onSubmit={handleSubmit}>
        <div className="search-container">
          <input
            type="number"
            value={teamId}
            onChange={(e) => setTeamId(e.target.value)}
            placeholder="Enter Team ID"
            disabled={loading}
          />
          <button type="submit" disabled={loading}>
            {loading ? 'Loading...' : 'Analyze Team'}
          </button>
        </div>
      </form>
      <p className="info-text">Enter your FPL Team ID to get transfer recommendations</p>
    </div>
  );
};

export default TeamSearch;
