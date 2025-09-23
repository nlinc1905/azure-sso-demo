import NextAuth, { Session } from "next-auth";
import AzureADProvider from "next-auth/providers/azure-ad";

// Extend the Session type to include accessToken
declare module "next-auth" {
  interface Session {
    accessToken?: string | null;
    idToken?: string | null;
  }
}

/** 
 * NextAuth configuration for Azure AD authentication.
 * This setup includes JWT and session callbacks to handle access tokens and user emails.
 * Make sure to set the environment variables AZURE_AD_CLIENT_ID, AZURE_AD_CLIENT_SECRET, and AZURE_AD_TENANT_ID.
 * The access token is stored in the JWT and made available in the session for API calls.
 * The user's email is also extracted from the profile and stored in the session.
 */
const handler = NextAuth({
  providers: [
    AzureADProvider({
      clientId: process.env.AZURE_AD_CLIENT_ID!,
      clientSecret: process.env.AZURE_AD_CLIENT_SECRET!,
      tenantId: process.env.AZURE_AD_TENANT_ID!,
    }),
  ],
  callbacks: {
    /**
     * JWT callback to include access token in the token object.
     * @param param0 - The JWT callback parameters.
     * @returns The updated token object.
     */
    async jwt({ token, account, profile }) {
      if (account) {
        token.idToken = account.id_token as string;
        token.accessToken = account.access_token as string;
        token.email = profile?.email
      }
      return token
    },
    /**
     * Session callback to include user email, ID token, and access token in the session object.
     * @param param0 - The session callback parameters.
     * @returns The updated session object.
     */
    async session({ session, token }) {
      if (token?.email) {
        session.user = session.user ?? {};
        session.user.email = token.email;
      }
      if (token?.accessToken) session.accessToken = token.accessToken as string;
      if (token?.idToken) session.idToken = token.idToken as string;
      return session
    },
  },
})

export { handler as GET, handler as POST };
