import { auditLog } from '../logger.js';

export const emailActions = {
  send_email: async (args) => {
    const { to, subject, body } = args;
    const isDryRun = process.env.DRY_RUN === 'true';

    if (isDryRun) {
      const result = { status: 'DRY_RUN_SUCCESS', message: 'Email not sent (Dry Run mode active).' };
      auditLog('send_email', args, result);
      return result;
    }

    // In production, integrate with SendGrid, Mailgun, or Gmail API here
    const result = { status: 'SUCCESS', message: `Email sent to ${to}` };
    auditLog('send_email', args, result);
    return result;
  },

  draft_email: async (args) => {
    const { to, subject, body } = args;
    // Drafting is usually a safe action, but we still log it
    const result = { status: 'SUCCESS', message: `Draft saved for ${to}` };
    auditLog('draft_email', args, result);
    return result;
  }
};
