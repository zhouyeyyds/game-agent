export interface User {
  id: string
  email: string
  displayName: string
}

export interface GameListItem {
  id: string
  title: string
  description: string
  coverUrl: string | null
  status: string
  author: {
    id: string
    displayName: string
  }
  tags: string[]
  publishedAt: string | null
  playCount: number
}

export interface PlayDescriptor {
  gameId: string
  description: string
  coverUrl: string | null
  tags: string[]
  publishedAt: string | null
  playCount: number
  title: string
  runtime: 'iframe_manifest_v1'
  manifestUrl: string
  storagePrefix: string
  sandbox: {
    allowScripts: boolean
    allowSameOrigin: boolean
    allowForms: boolean
    allowPopups: boolean
  }
}

export interface GameManifest {
  schemaVersion: 'game-manifest-v1'
  gameId: string
  versionId: string
  title: string
  entry: string
  entryUrl: string
  assets: Array<{
    name: string
    url: string
    contentType: string
  }>
  permissions: {
    network: boolean
    storage: boolean
  }
}
