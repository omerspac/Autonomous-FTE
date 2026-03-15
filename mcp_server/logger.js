import fs from 'fs';
import path from 'path';

const LOG_FILE = path.join(process.cwd(), 'audit_log.jsonl');

/**
 * Audit Logger for MCP Actions
 * Format: { timestamp, action_type, actor, parameters, approval_status, result }
 */
export const auditLog = (action_type, parameters, result, approval_status = 'approved') => {
  const entry = {
    timestamp: new Date().toISOString(),
    action_type,
    actor: 'AI_Employee_Orchestrator',
    parameters,
    approval_status,
    result
  };

  const logLine = JSON.stringify(entry) + '\n';
  
  // Log to console for visibility
  console.error(`[AUDIT] ${action_type}: ${JSON.stringify(parameters)} -> ${JSON.stringify(result)}`);

  // Append to file
  fs.appendFileSync(LOG_FILE, logLine);
};
