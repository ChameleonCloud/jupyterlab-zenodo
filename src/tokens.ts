import { Token } from '@phosphor/coreutils';

export class ZenodoRecord {
  readonly doi: string;

  readonly path: string;
}

export class ZenodoPost {
  readonly title: string;

  readonly author: string;

  readonly affiliation: string;

  readonly description: string;

  readonly directory?: string;

  readonly zenodoToken?: string;
}

/* tslint:disable */
export const IZenodoRegistry = new Token<IZenodoRegistry>(
  '@jupyterlab_zenodo:IZenodoRegistry'
)
/* tslint:enable */

export interface IZenodoRegistry {
  updateDeposition(path: string): Promise<ZenodoRecord>;
  createDeposition(path: string, post: ZenodoPost): Promise<ZenodoRecord>;
  getDepositions(): Promise<ZenodoRecord[]>;
  hasDepositionSync(path: string): boolean;
  getDepositionSync(path: string): ZenodoRecord | undefined;
}
