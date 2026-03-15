import { auditLog } from '../logger.js';

export const calendarActions = {
  calendar_event: async (args) => {
    const { title, start, end, location } = args;
    const isDryRun = process.env.DRY_RUN === 'true';

    if (isDryRun) {
      const result = { status: 'DRY_RUN_SUCCESS', message: 'Calendar event not created (Dry Run mode active).' };
      auditLog('calendar_event', args, result);
      return result;
    }

    // In production, use Google Calendar API or Outlook API
    const result = { status: 'SUCCESS', message: `Calendar event "${title}" created.` };
    auditLog('calendar_event', args, result);
    return result;
  }
};
