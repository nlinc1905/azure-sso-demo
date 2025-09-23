"use client";

import { useSession, signIn, signOut } from "next-auth/react"

export default function Home() {
  const sessionHook = useSession()
  const session = sessionHook.data
  const status = sessionHook.status

  // Function to call the protected FastAPI endpoint
  // This function uses the ID token from the session to authenticate the request
  async function callApi() {
    if (!session?.idToken) return
    const res = await fetch("http://localhost:8000/protected", {
      headers: {
        Authorization: `Bearer ${session.idToken}`,
      },
    })
    const data = await res.json()
    // Display the response from the FastAPI endpoint
    alert(JSON.stringify(data, null, 2))
  }

  if (status === "loading") {
    return <div>Loading...</div>
  }

  // If not signed in, display a sign-in button
  if (status === "unauthenticated") {
    return (
      <div>
        <h1>Welcome</h1>
        <button onClick={() => signIn("azure-ad")}>Click here to sign in with Azure</button>
      </div>
    )
  }

  // If signed in, display the user's email and buttons to call the API and sign out
  return (
    <div>
      {session ? <h1>Hello {session.user?.email}</h1> : <h1>Loading session...</h1>}
      <button onClick={() => callApi()}>Click here to call FastAPI</button>
      <br /><br />
      <button onClick={() => signOut()}>Click here to sign out</button>
    </div>
  )
}
