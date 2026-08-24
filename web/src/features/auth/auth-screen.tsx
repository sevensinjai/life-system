/** Register or log in. Either one hands back a token and drops you inside. */

import { useState } from "react"
import { useMutation } from "@tanstack/react-query"
import { toast } from "sonner"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { useApi } from "@/hooks/use-api"
import { localTimezone } from "@/lib/format"
import type { TokenResponse } from "@/lib/types"

export function AuthScreen() {
  const { api, signIn } = useApi()

  const [login, setLogin] = useState({ email: "", password: "" })
  const [registration, setRegistration] = useState({
    email: "",
    password: "",
    name: "",
    timezone: localTimezone(),
  })

  const enter = (token: TokenResponse, message: string) => {
    toast.success(message)
    signIn(token.access_token)
  }

  const loginMutation = useMutation({
    mutationFn: () => api.login(login),
    onSuccess: (token) => enter(token, "Welcome back."),
  })

  const registerMutation = useMutation({
    mutationFn: () => api.register(registration),
    onSuccess: (token) => enter(token, "Player created. The System is watching."),
  })

  return (
    <div className="grid gap-6">
      <div className="grid gap-1 pt-4 text-center">
        <h1 className="text-2xl font-semibold tracking-tight">Awaken</h1>
        <p className="text-muted-foreground text-sm">
          Run your life like a progression RPG.
        </p>
      </div>

      <Tabs defaultValue="login">
        <TabsList className="w-full">
          <TabsTrigger value="login" className="flex-1">
            Log in
          </TabsTrigger>
          <TabsTrigger value="register" className="flex-1">
            Register
          </TabsTrigger>
        </TabsList>

        <TabsContent value="login">
          <form
            className="grid gap-4 pt-4"
            onSubmit={(event) => {
              event.preventDefault()
              loginMutation.mutate()
            }}
          >
            <div className="grid gap-2">
              <Label htmlFor="login-email">Email</Label>
              <Input
                id="login-email"
                type="email"
                inputMode="email"
                autoComplete="username"
                required
                value={login.email}
                onChange={(event) => setLogin({ ...login, email: event.target.value })}
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="login-password">Password</Label>
              <Input
                id="login-password"
                type="password"
                autoComplete="current-password"
                required
                value={login.password}
                onChange={(event) => setLogin({ ...login, password: event.target.value })}
              />
            </div>
            <Button type="submit" className="w-full" disabled={loginMutation.isPending}>
              Enter the System
            </Button>
          </form>
        </TabsContent>

        <TabsContent value="register">
          <form
            className="grid gap-4 pt-4"
            onSubmit={(event) => {
              event.preventDefault()
              registerMutation.mutate()
            }}
          >
            <div className="grid gap-2">
              <Label htmlFor="register-email">Email</Label>
              <Input
                id="register-email"
                type="email"
                inputMode="email"
                autoComplete="username"
                required
                value={registration.email}
                onChange={(event) =>
                  setRegistration({ ...registration, email: event.target.value })
                }
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="register-password">Password</Label>
              <Input
                id="register-password"
                type="password"
                autoComplete="new-password"
                minLength={8}
                required
                value={registration.password}
                onChange={(event) =>
                  setRegistration({ ...registration, password: event.target.value })
                }
              />
              <p className="text-muted-foreground text-xs">At least 8 characters.</p>
            </div>
            <div className="grid gap-2">
              <Label htmlFor="register-name">Hunter name</Label>
              <Input
                id="register-name"
                maxLength={80}
                required
                value={registration.name}
                onChange={(event) =>
                  setRegistration({ ...registration, name: event.target.value })
                }
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="register-timezone">Timezone</Label>
              <Input
                id="register-timezone"
                spellCheck={false}
                required
                value={registration.timezone}
                onChange={(event) =>
                  setRegistration({ ...registration, timezone: event.target.value })
                }
              />
              <p className="text-muted-foreground text-xs">
                IANA name; quests reset at midnight here.
              </p>
            </div>
            <Button type="submit" className="w-full" disabled={registerMutation.isPending}>
              Awaken
            </Button>
          </form>
        </TabsContent>
      </Tabs>

      <p className="text-muted-foreground text-center text-xs">
        The token is kept on this device. Set the API target from the gear icon.
      </p>
    </div>
  )
}
